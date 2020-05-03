/*
 * Copyright (c) 2020 Jonathan Afek <jonyafek@me.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdint.h>
#include <string.h>

#include "aleph_fbuc_dev.h"
#include "aleph_fbuc_mclass.h"
#include "kern_funcs.h"
#include "utils.h"
#include "mclass_reg.h"

#include "hw/arm/guest-services/general.h"


static uint8_t aleph_fbuc_meta_class_inst[ALEPH_MCLASS_SIZE];

void *get_fbuc_mclass_inst(void)
{
    return (void *)&aleph_fbuc_meta_class_inst[0];
}

static FBUCMembers *get_fbuc_members(void *fbuc)
{
    FBUCMembers *members;
    members = (FBUCMembers *)&((uint8_t *)fbuc)[FBUC_MEMBERS_OFFSET];
    return members;
}

static void fbuc_install_external_method(void *fbuc,
                                         IOExternalMethodAction func,
                                         uint64_t index,
                                         uint32_t scic,
                                         uint32_t stic,
                                         uint32_t scoc,
                                         uint32_t stoc)
{
    if (index >= FBUC_MAX_EXT_FUNCS) {
        cancel();
    }
    FBUCMembers *members = get_fbuc_members(fbuc);
    members->fbuc_external_methods[index].function = func;
    members->fbuc_external_methods[index].checkScalarInputCount = scic;
    members->fbuc_external_methods[index].checkStructureInputSize = stic;
    members->fbuc_external_methods[index].checkScalarOutputCount = scoc;
    members->fbuc_external_methods[index].checkStructureOutputSize = stoc;
}

static uint64_t fbuc_ext_meth_get_layer_default_sur(void *target,
                                                    void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_get_layer_default_sur()!!!", 0);
    arguments->scalarOutput[0] = 1;
    log_uint64("arguments->scalarOutput[0]", arguments->scalarOutput[0]);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    log_uint64("arguments->scalarInput[1]", arguments->scalarInput[1]);
    return 0;
}

static uint64_t fbuc_ext_meth_swap_begin(void *target, void *reference,
                                         IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    log_uint64("fbuc_ext_meth_swap_begin()!!!", arguments->scalarOutput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_swap_end(void *target, void *reference,
                                       IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_swap_end()!!!", 0);
    log_uint64("((uint64_t *)arguments->structureInput)[0]",
               ((uint64_t *)arguments->structureOutput)[0]);
    log_uint64("((uint64_t *)arguments->structureInput)[1]",
               ((uint64_t *)arguments->structureOutput)[1]);
    log_uint64("((uint64_t *)arguments->structureInput)[2]",
               ((uint64_t *)arguments->structureOutput)[2]);
    log_uint64("((uint64_t *)arguments->structureInput)[37]",
               ((uint64_t *)arguments->structureOutput)[37]);
    log_uint64("((uint64_t *)arguments->structureInput)[38]",
               ((uint64_t *)arguments->structureOutput)[38]);
    log_uint64("((uint64_t *)arguments->structureInput)[39]",
               ((uint64_t *)arguments->structureOutput)[39]);
    log_uint64("((uint64_t *)arguments->structureInput)[40]",
               ((uint64_t *)arguments->structureOutput)[40]);
    log_uint64("((uint64_t *)arguments->structureInput)[41]",
               ((uint64_t *)arguments->structureOutput)[41]);
    log_uint64("((uint64_t *)arguments->structureInput)[42]",
               ((uint64_t *)arguments->structureOutput)[42]);
    log_uint64("((uint64_t *)arguments->structureInput)[43]",
               ((uint64_t *)arguments->structureOutput)[43]);
    log_uint64("((uint64_t *)arguments->structureInput)[76]",
               ((uint64_t *)arguments->structureOutput)[76]);
    log_uint64("((uint64_t *)arguments->structureInput)[77]",
               ((uint64_t *)arguments->structureOutput)[77]);
    log_uint64("((uint64_t *)arguments->structureInput)[78]",
               ((uint64_t *)arguments->structureOutput)[78]);
    log_uint64("fbuc_ext_meth_swap_end()!!! arguments->structureInputSize: ",
               arguments->structureInputSize);
    return 0;
}

static uint64_t fbuc_ext_meth_swap_wait(void *target, void *reference,
                                        IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_swap_wait()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    log_uint64("arguments->scalarInput[1]", arguments->scalarInput[1]);
    log_uint64("arguments->scalarInput[2]", arguments->scalarInput[2]);
    return 0;
}

static uint64_t fbuc_ext_meth_get_id(void *target, void *reference,
                                     IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 2;
    log_uint64("fbuc_ext_meth_get_id()!!!", arguments->scalarOutput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_get_disp_size(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_get_disp_size()!!!", 0);
    //TODO: get this input somehow
    arguments->scalarOutput[0] = 600;
    arguments->scalarOutput[1] = 800;
    return 0;
}

static uint64_t fbuc_ext_meth_req_power_change(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_req_power_change()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_set_debug_flags(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    log_uint64("fbuc_ext_meth_set_debug_flags()!!!", arguments->scalarOutput[0]);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    log_uint64("arguments->scalarInput[1]", arguments->scalarInput[1]);
    return 0;
}

static uint64_t fbuc_ext_meth_set_gamma_table(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_set_gamma_table()!!!", 0);
    log_uint64("((uint64_t *)arguments->structureOutput)[0]",
               ((uint64_t *)arguments->structureOutput)[0]);
    log_uint64("((uint64_t *)arguments->structureOutput)[1]",
               ((uint64_t *)arguments->structureOutput)[1]);
    return 0;
}

static uint64_t fbuc_ext_meth_is_main_disp(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    log_uint64("fbuc_ext_meth_is_main_disp()!!!", arguments->scalarOutput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_set_display_dev(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_set_display_dev()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_get_gamma_table(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_get_gamma_table()!!!", 0);
    for (int i = 0; i < arguments->structureOutputSize; i++) {
        ((uint8_t *)arguments->structureOutput)[i] = 0x7f;
    }
    return 0;
}

static uint64_t fbuc_ext_meth_get_dot_pitch(void *target,
                                            void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //arguments->scalarOutput[0] = 152;
    arguments->scalarOutput[0] = 0;
    log_uint64("fbuc_ext_meth_get_dot_pitch()!!!", arguments->scalarOutput[0]);
    //TODO: get this input somehow
    return 0;
}

static uint64_t fbuc_ext_meth_en_dis_vid_power_save(void *target,
                                                    void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_en_dis_vid_power_save()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_surface_is_rep(void *target,
                                             void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_surface_is_rep()!!!", 0);
    arguments->scalarOutput[0] = 1;
    log_uint64("arguments->scalarOutput[0]", arguments->scalarOutput[0]);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_set_bright_corr(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_set_bright_corr()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_set_matrix(void *target,
                                         void *reference,
                                         IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_set_matrix()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    log_uint64("((uint64_t *)arguments->structureInput)[0]",
               ((uint64_t *)arguments->structureOutput)[0]);
    log_uint64("((uint64_t *)arguments->structureInput)[1]",
               ((uint64_t *)arguments->structureOutput)[1]);
    return 0;
}

static uint64_t fbuc_ext_meth_get_color_remap_mode(void *target,
                                                   void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 6;
    //TODO: this might need to be changed. not sure what the numbers mean
    log_uint64("fbuc_ext_meth_get_color_remap_mode()!!!", arguments->scalarOutput[0]);
    //arguments->scalarOutput[0] = 6;
    return 0;
}

static uint64_t fbuc_ext_meth_set_parameter(void *target,
                                            void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_set_parameter()!!!", 0);
    log_uint64("arguments->scalarInput[0]", arguments->scalarInput[0]);
    log_uint64("((uint64_t *)arguments->structureInput)[0]",
               ((uint64_t *)arguments->structureOutput)[0]);
    return 0;
}

static uint64_t fbuc_ext_meth_enable_notifications(void *target,
                                                   void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //TODO: actually implement this to enable tofications
    FBUCMembers *members = get_fbuc_members(target);
    log_uint64("fbuc_ext_meth_enable_notifications()!!!",
               arguments->scalarInput[0]);
    log_uint64("fbuc_ext_meth_enable_notifications()!!!",
               arguments->scalarInput[1]);
    log_uint64("fbuc_ext_meth_enable_notifications()!!!",
               arguments->scalarInput[2]);
    log_uint64("fbuc_ext_meth_enable_notifications()!!!",
               arguments->scalarInput[3]);
    uint64_t cb = arguments->scalarInput[0];
    uint64_t ref = arguments->scalarInput[1];
    uint64_t type = arguments->scalarInput[2];
    IOUserClient_setAsyncReference64(&members->notif_ports[type].asnyc_ref64[0],
                                     members->notif_ports[type].port,
                                     cb, ref, members->task);
    log_uint64("test()!!!", 3);
    return 0;
}

static uint64_t fbuc_ext_meth_change_frame_info(void *target,
                                                void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //TODO: actually implement this
    FBUCMembers *members = get_fbuc_members(target);
    log_uint64("fbuc_ext_meth_change_frame_info()!!!",
               arguments->scalarInput[0]);
    log_uint64("fbuc_ext_meth_change_frame_info()!!!",
               arguments->scalarInput[1]);

    //uint64_t args[2];
    //uint64_t type = arguments->scalarInput[0];
    //args[0] = type;
    //args[1] = arguments->scalarInput[1];
    //IOUserClient_sendAsyncResult64(&members->notif_ports[type].asnyc_ref64[0],
    //                               0, &args[0], 2);
    uint64_t args[6];
    uint64_t type = arguments->scalarInput[0];
    args[0] = 5;
    args[1] = 6;
    args[2] = 7;
    args[3] = 8;
    args[4] = 9;
    args[5] = 10;
    IOUserClient_sendAsyncResult64(&members->notif_ports[type].asnyc_ref64[0],
                                   0, &args[0], 6);
    return 0;
}

static uint64_t fbuc_ext_meth_supported_frame_info(void *target,
                                                   void *reference,
                                          IOExternalMethodArguments *arguments)
{
    log_uint64("fbuc_ext_meth_supported_frame_info()!!!",
               arguments->scalarInput[0]);

    //Ugly trick we have to do because of how we compile this code
    switch (arguments->scalarInput[0])
    {
        case 0:
        strncpy(arguments->structureOutput, "Blend_CRC",
                arguments->structureOutputSize);
        break;
        case 1:
        strncpy(arguments->structureOutput, "Dither_CRC",
                arguments->structureOutputSize);
        break;
        case 2:
        strncpy(arguments->structureOutput, "Presentation_time",
                arguments->structureOutputSize);
        break;
        case 3:
        strncpy(arguments->structureOutput, "Presentation_delta",
                arguments->structureOutputSize);
        break;
        case 4:
        strncpy(arguments->structureOutput, "Requested_presentation",
                arguments->structureOutputSize);
        break;
        case 5:
        strncpy(arguments->structureOutput, "Performance_headroom",
                arguments->structureOutputSize);
        break;
        case 6:
        strncpy(arguments->structureOutput, "Thermal_throttle",
                arguments->structureOutputSize);
        break;
        case 7:
        strncpy(arguments->structureOutput, "Flags",
                arguments->structureOutputSize);
        break;
        default:
        cancel();
    }

    arguments->scalarOutput[0] = 8;
    return 0;
}

//virtual functions of our driver
void *fbuc_getMetaClass(void *this)
{
    return get_fbuc_mclass_inst();
}

uint64_t fbuc_start(void *this)
{
    fbuc_install_external_method(this, &fbuc_ext_meth_get_layer_default_sur,
                                 3, 2, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_swap_begin,
                                 4, 0, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_swap_end,
                                 5, 0, -1, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_swap_wait,
                                 6, 3, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_get_id, 7, 0, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_get_disp_size,
                                 8, 0, 0, 2, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_req_power_change,
                                 12, 1, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_debug_flags,
                                 15, 2, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_gamma_table,
                                 17, 0, 3084, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_is_main_disp,
                                 18, 0, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_display_dev,
                                 22, 1, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_get_gamma_table,
                                 27, 0, 0, 0, 3084);
    fbuc_install_external_method(this, &fbuc_ext_meth_get_dot_pitch,
                                 28, 0, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_en_dis_vid_power_save,
                                 33, 1, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_surface_is_rep,
                                 49, 1, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_bright_corr,
                                 50, 1, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_matrix,
                                 55, 1, 72, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_get_color_remap_mode,
                                 57, 0, 0, 1, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_set_parameter,
                                 68, 1, 8, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_enable_notifications,
                                 72, 4, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_change_frame_info,
                                 73, 2, 0, 0, 0);
    fbuc_install_external_method(this, &fbuc_ext_meth_supported_frame_info,
                                 74, 1, 0, 1, 64);
    return IOService_start(this);
}

uint64_t fbuc_externalMethod(void *this, uint32_t selector,
                             IOExternalMethodArguments *args,
                             IOExternalMethodDispatch *dispatch,
                             void *target, void *reference)
{
    IOExternalMethodDispatch *new_dispatch;
    FBUCMembers *members = get_fbuc_members(this);

    log_uint64("---------------------------------------------", 0);
    log_uint64("fbuc_externalMethod() target: ", (uint64_t)target);
    log_uint64("fbuc_externalMethod() reference: ", (uint64_t)reference);
    log_uint64("---------------------------------------------", 0);
    log_uint64("fbuc_externalMethod() selector: ", selector);
    log_uint64("fbuc_externalMethod() args->version: ",
               (uint64_t)args->version);
    log_uint64("fbuc_externalMethod() args->selector: ",
               (uint64_t)args->selector);
    log_uint64("fbuc_externalMethod() args->unknown1[0]: ",
               args->unknown1[0]);
    log_uint64("fbuc_externalMethod() args->unknown1[1]: ",
               args->unknown1[1]);
    log_uint64("fbuc_externalMethod() args->unknown1[2]: ",
               args->unknown1[2]);
    log_uint64("fbuc_externalMethod() args->scalarInput: ",
               (uint64_t)args->scalarInput);
    log_uint64("fbuc_externalMethod() args->scalarInputCount: ",
               args->scalarInputCount);
    log_uint64("fbuc_externalMethod() args->align1: ",
               args->align1);
    log_uint64("fbuc_externalMethod() args->structureInput: ",
               (uint64_t)args->structureInput);
    log_uint64("fbuc_externalMethod() args->structureInputSize: ",
               args->structureInputSize);
    log_uint64("fbuc_externalMethod() args->align2: ",
               args->align2);
    log_uint64("fbuc_externalMethod() args->structureInputDescriptor: ",
               (uint64_t)args->structureInputDescriptor);
    log_uint64("fbuc_externalMethod() args->scalarOutput: ",
               (uint64_t)args->scalarOutput);
    log_uint64("fbuc_externalMethod() args->scalarOutputCount: ",
               args->scalarOutputCount);
    log_uint64("fbuc_externalMethod() args->align3: ",
               args->align3);
    log_uint64("fbuc_externalMethod() args->structureOutput: ",
               (uint64_t)args->structureOutput);
    log_uint64("fbuc_externalMethod() args->structureOutputSize: ",
               args->structureOutputSize);
    log_uint64("fbuc_externalMethod() args->align4: ",
               args->align4);
    log_uint64("fbuc_externalMethod() args->structureOutputDescriptor: ",
               (uint64_t)args->structureOutputDescriptor);
    log_uint64("---------------------------------------------", 0);

    if ((selector >= FBUC_MAX_EXT_FUNCS) ||
        (0 == members->fbuc_external_methods[selector].function)) {
        log_uint64("ERR fbuc_externalMethod() no func selector: ", selector);
        cancel();
    }
    new_dispatch = &members->fbuc_external_methods[selector];
    return IOUserClient_externalMethod(this, selector, args, new_dispatch,
                                       this, reference);
}

uint64_t fbuc_clientClose(void *this)
{
    log_uint64("fbuc_clientClose!!", 0);
    void **vtable_ptr = (void **)*(uint64_t *)this;
    FuncIOSerivceTerminate vfunc_terminate =
        (FuncIOSerivceTerminate)vtable_ptr[IOSERVICE_TERMINATE_INDEX];
    vfunc_terminate(this, 0);
    return 0;
}

uint64_t fbuc_connectClient(void *this, void *user_client)
{
    log_uint64("fbuc_connectClient not supported", 0);
    cancel();
    return 0;
}

uint64_t fbuc_getNotificationSemaphore(void *this, uint64_t type, void *sem)
{
    log_uint64("fbuc_getNotificationSemaphore not supported", 0);
    cancel();
    return 0;
}

uint64_t fbuc_clientMemoryForType(void *this, uint64_t type, void *opts,
                                  void **mem)
{
    log_uint64("fbuc_clientMemoryForType not supported", 0);
    cancel();
    return 0;
}

uint64_t fbuc_registerNotificationPort(void *this, void *port,
                                       uint64_t type, uint64_t ref)
{
    log_uint64("fbuc_registerNotificationPort!!", type);
    FBUCMembers *members = get_fbuc_members(this);
    if (type >= FBUC_MAX_NOTIF_PORTS) {
        cancel();
    }
    members->notif_ports[type].type = type;
    members->notif_ports[type].port = port;
    members->notif_ports[type].ref = ref;
    return 0;
}

uint64_t fbuc_initWithTask(void *this, void *task, void *sid, uint64_t type)
{
    log_uint64("fbuc_initWithTask!!", (uint64_t)task);
    FBUCMembers *members = get_fbuc_members(this);
    members->task = task;
    return IOUserClient_initWithTask(this, task, sid, type);
}

uint64_t fbuc_destructor(void *this)
{
    log_uint64("fbuc_destructor!!", 0);
    void *obj = IOUserClient_destructor(this);
    OSObject_delete(obj, ALEPH_FBUC_SIZE);
    return 0;
}
