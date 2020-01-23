#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>

#include "hw/arm/guest-services/general.h"

#define DIR_IN 1
#define DIR_OUT 2

typedef struct {
    int fd;
    int *error;

    int (*close)(int fd);
    int (*fcntl)(int fd, int cmd, ...);

    int (*socket)(int domain, int type, int protocol);
    int (*accept)(int sckt, struct sockaddr *addr, socklen_t *addrlen);
    int (*bind)(int sckt, const struct sockaddr *addr, socklen_t addrlen);
    int (*connect)(int sckt, const struct sockaddr *addr, socklen_t addrlen);
    int (*listen)(int sckt, int backlog);
    ssize_t (*recv)(int sckt, void *buffer, size_t length, int flags);
    ssize_t (*send)(int sckt, const void *buffer, size_t length, int flags);
} socket_t;

static void init_qemu_socket(socket_t *sock_struct);
static void init_native_socket(socket_t *sock_struct);
static void terminate(int signum);
static int usage(const char *prog_name);
static int parse_address_spec(char* address_spec, uint32_t *listen_port,
                              char *target_ip, size_t target_ip_size,
                              uint32_t *target_port);
static int send_receive(socket_t *in, socket_t *out);
static int handle_incoming_connection(socket_t *in, socket_t *out,
                                      const char *target_ip,
                                      uint32_t target_port);
static int tunnel(socket_t *s_listen, socket_t *in, socket_t *out,
                  uint32_t listen_port, char *target_ip, uint32_t target_port);

static socket_t s_listen = {.fd = -1}, s_in = {.fd = -1}, s_out = {.fd = -1};
static int daemonize = 0;

int main(int argc, char *argv[])
{
    uint32_t listen_port = 0, target_port = 0;
    char target_ip[30];
    struct sigaction action;
    int direction;

    switch (argc) {
    case 2:
        break;
    case 3:
        if (!strncmp(argv[1], "-d", strlen("-d")) ||
            !strncmp(argv[1], "--daemonize", strlen("--daemonize"))) {
                daemonize = 1;
                break;
            }
    default:
        return usage(argv[0]);
    }

    direction = parse_address_spec(argv[argc - 1], &listen_port, target_ip,
                                   sizeof(target_ip), &target_port);
    if (direction < 0)
    {
        return usage(argv[0]);
    }

    memset(&action, 0, sizeof(struct sigaction));
    action.sa_handler = terminate;
    sigaction(SIGTERM, &action, NULL);


    if (DIR_IN == direction) {
        init_qemu_socket(&s_listen);
        init_qemu_socket(&s_in);
        init_native_socket(&s_out);

        return tunnel(&s_listen, &s_in, &s_out, listen_port, target_ip,
                      target_port);
    } else if (DIR_OUT == direction) {
        init_native_socket(&s_listen);
        init_native_socket(&s_in);
        init_qemu_socket(&s_out);

        return tunnel(&s_listen, &s_in, &s_out, listen_port, target_ip,
                      target_port);
    } else {
        return usage(argv[0]);
    }
}

static void init_qemu_socket(socket_t *sock_struct)
{
    if (sock_struct) {
        sock_struct->error   = &guest_svcs_errno;

        sock_struct->close   = &qc_close;
        sock_struct->fcntl   = &qc_fcntl;

        sock_struct->socket  = &qc_socket;
        sock_struct->accept  = &qc_accept;
        sock_struct->bind    = &qc_bind;
        sock_struct->connect = &qc_connect;
        sock_struct->listen  = &qc_listen;
        sock_struct->recv    = &qc_recv;
        sock_struct->send    = &qc_send;
    }
}

static void init_native_socket(socket_t *sock_struct)
{
    if (sock_struct) {
        sock_struct->error   = &errno;

        sock_struct->close   = &close;
        sock_struct->fcntl   = &fcntl;

        sock_struct->socket  = &socket;
        sock_struct->accept  = &accept;
        sock_struct->bind    = &bind;
        sock_struct->connect = &connect;
        sock_struct->listen  = &listen;
        sock_struct->recv    = &recv;
        sock_struct->send    = &send;
    }
}

static void terminate(int signum)
{
    if (s_out.fd != -1) {
        fprintf(stderr, "Closing outward socket...\n");
        s_out.close(s_out.fd);
    }

    if (s_in.fd != -1) {
        fprintf(stderr, "Closing inward socket...\n");
        s_in.close(s_in.fd);
    }

    if (s_listen.fd != -1) {
        fprintf(stderr, "Closing listening socket...\n");
        s_listen.close(s_listen.fd);
    }

    exit(0);
}

static int usage(const char *prog_name)
{
    fprintf(stderr, "Usage: %s [-d|--daemonize] [<in|out>:]listen-port:target-ip:target-port\n",
            prog_name);

    return -1;
}

static int parse_address_spec(char* address_spec, uint32_t *listen_port,
                              char *target_ip, size_t target_ip_size,
                              uint32_t *target_port)
{
    char *token = strtok(address_spec, ":");
    int direction = DIR_IN;

    if (NULL != token) {
        if (!strncmp(token, "out", strlen("out"))) {
            direction = DIR_OUT;
            token = strtok(NULL, ":");
        } else if (!strncmp(token, "in", strlen("in"))) {
            direction = DIR_IN;
            token = strtok(NULL, ":");
        }
    }

    if (NULL != token) {
        errno = 0;
        *listen_port = (uint32_t) strtoul(token, NULL, 0);

        if (errno) {
            fprintf(stderr, "Couldn't parse the listen port argument (%s)!\n",
                    token);
            return -1;
        }

        token = strtok(NULL, ":");
    }

    if (NULL != token) {
        strncpy(target_ip, token, target_ip_size);
        token = strtok(NULL, ":");
    }

    if (NULL != token) {
        errno = 0;
        *target_port = (uint32_t) strtoul(token, NULL, 0);

        if (errno) {
            fprintf(stderr, "Couldn't parse the target port argument (%s)!\n",
                    token);
            return -1;
        }

        token = strtok(NULL, ":");
    }

    if (NULL != token) {
        fprintf(stderr, "Garbage after address spec (%s)!\n", token);
        return -1;
    }

    return direction;
}

static int send_receive(socket_t *in, socket_t *out)
{
    int retval;
    uint8_t buffer[MAX_BUF_SIZE];

    for (;;) {
        if ((retval = in->recv(in->fd, buffer, sizeof(buffer), 0)) > 0) {
            // Data received!
            if (out->send(out->fd, buffer, retval, 0) < 0) {
                // Couldn't send!
                out->close(out->fd);
                return 0;
            }
        } else if (0 == retval) {
            // Remote socket closed!
            out->close(out->fd);
            return 0;
        } else {
            if ((*(in->error) != EAGAIN) && \
                (*(in->error) != EWOULDBLOCK))
            {
                // Remote socket error!
                out->close(out->fd);
                return 0;
            }
            // No data yet
        }

        if ((retval = out->recv(out->fd, buffer, sizeof(buffer), 0)) > 0) {
            // Data received!
            if (in->send(in->fd, buffer, retval, 0) < 0) {
                // Couldn't send!
                out->close(out->fd);
                return 0;
            }
        } else if (0 == retval) {
            // Target socket closed!
            out->close(out->fd);
            return 0;
        } else {
            if ((*(out->error) != EAGAIN) && \
                (*(out->error) != EWOULDBLOCK))
            {
                // Target socket error!
                out->close(out->fd);
                return 0;
            }
            // No data yet
        }
    }
}

static int handle_incoming_connection(socket_t *in, socket_t *out,
                                      const char *target_ip,
                                      uint32_t target_port)
{
    int flags;
    struct sockaddr_in target;

    if ((out->fd = out->socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        fprintf(stderr, "socket failed: %d\n", *(out->error));
        return -1;
    }

    target.sin_family = AF_INET;
    target.sin_port = htons(target_port);

    if (inet_pton(AF_INET, target_ip, &target.sin_addr) <= 0) {
        fprintf(stderr, "inet_pton failed: %d\n", errno);
        out->close(out->fd);
        return -1;
    }

    if (out->connect(out->fd, (struct sockaddr *) &target, sizeof(target)) < 0) {
        fprintf(stderr, "connect failed: %d\n", *(out->error));
        out->close(out->fd);
        return -1;
    }

    if ((flags = out->fcntl(out->fd, F_GETFL)) < 0) {
        fprintf(stderr, "fcntl[F_GETFL] failed: %d\n", *(out->error));
        out->close(out->fd);
        return -1;
    }

    if (out->fcntl(out->fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        fprintf(stderr, "fcntl[F_SETFL] failed: %d\n", *(out->error));
        out->close(out->fd);
        return -1;
    }

    return send_receive(in, out);
}

static int tunnel(socket_t *s_listen, socket_t *in, socket_t *out,
                  uint32_t listen_port, char *target_ip, uint32_t target_port)
{
    int flags, process_id;
    struct sockaddr_in local, remote;
    socklen_t remotelen = sizeof(remote);
    
    if ((s_listen->fd = s_listen->socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        fprintf(stderr, "socket failed: %d\n", *(s_listen->error));
        return -1;
    }

    if ((flags = s_listen->fcntl(s_listen->fd, F_GETFL)) < 0) {
        fprintf(stderr, "fcntl[F_GETFL] failed: %d\n", *(s_listen->error));
        s_listen->close(s_listen->fd);
        return -1;
    }

    if (s_listen->fcntl(s_listen->fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        fprintf(stderr, "fcntl[F_SETFL] failed: %d\n", *(s_listen->error));
        s_listen->close(s_listen->fd);
        return -1;
    }

    local.sin_family = AF_INET;
    local.sin_port = htons(listen_port);
    local.sin_addr.s_addr = INADDR_ANY;
    if (s_listen->bind(s_listen->fd, (struct sockaddr*) &local,
                       sizeof(local)) < 0)
    {
        fprintf(stderr, "bind failed: %d\n", *(s_listen->error));
        s_listen->close(s_listen->fd);
        return -1;
    }

    if (s_listen->listen(s_listen->fd, 5) < 0) {
        fprintf(stderr, "listen failed: %d\n", *(s_listen->error));
        s_listen->close(s_listen->fd);
        return -1;
    }

    if (daemonize) {
        printf("Waiting for connections in the background...\n");
        if ((process_id = fork()) < 0) {
            fprintf(stderr, "Couldn't daemonize - continuing in foreground...\n");
        } else if (process_id > 0) {
            exit(0);
        } else {
            close(STDIN_FILENO);
        }
    }

    for (;;) {
        // Wait for an incoming connection...
        in->fd = s_listen->accept(s_listen->fd, (struct sockaddr*) &remote,
                                  &remotelen);

        if (in->fd < 0) {
            if ((*(in->error) != EAGAIN ) && \
                (*(in->error) != EWOULDBLOCK))
            {
                fprintf(stderr, "accept failed: %d\n", *(in->error));
                s_listen->close(s_listen->fd);
                return -1;
            } else {
                usleep(10000); // TODO: define!
            }
        } else {
            if (handle_incoming_connection(in, out, target_ip,
                                           target_port) < 0) {
                break;
            }

            in->close(in->fd);
        }
    }

    in->close(in->fd);
    s_listen->close(s_listen->fd);

    return 0;
}
