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
    arguments->scalarOutput[0] = 1;
    return 0;
}

static uint64_t fbuc_ext_meth_swap_begin(void *target, void *reference,
                                         IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    return 0;
}

static uint64_t fbuc_ext_meth_swap_end(void *target, void *reference,
                                       IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_swap_wait(void *target, void *reference,
                                        IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_get_id(void *target, void *reference,
                                     IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 2;
    return 0;
}

static uint64_t fbuc_ext_meth_get_disp_size(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //TODO: get this input somehow
    arguments->scalarOutput[0] = 600;
    arguments->scalarOutput[1] = 800;
    return 0;
}

static uint64_t fbuc_ext_meth_req_power_change(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_set_debug_flags(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    return 0;
}

static uint64_t fbuc_ext_meth_set_gamma_table(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_is_main_disp(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    return 0;
}

static uint64_t fbuc_ext_meth_set_display_dev(void *target, void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_get_gamma_table(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
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
    //TODO: get this input somehow
    return 0;
}

static uint64_t fbuc_ext_meth_en_dis_vid_power_save(void *target,
                                                    void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_surface_is_rep(void *target,
                                             void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 1;
    return 0;
}

static uint64_t fbuc_ext_meth_set_bright_corr(void *target,
                                              void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_set_matrix(void *target,
                                         void *reference,
                                         IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_get_color_remap_mode(void *target,
                                                   void *reference,
                                          IOExternalMethodArguments *arguments)
{
    arguments->scalarOutput[0] = 6;
    //TODO: this might need to be changed. not sure what the numbers mean
    //arguments->scalarOutput[0] = 6;
    return 0;
}

static uint64_t fbuc_ext_meth_set_parameter(void *target,
                                            void *reference,
                                          IOExternalMethodArguments *arguments)
{
    return 0;
}

static uint64_t fbuc_ext_meth_enable_notifications(void *target,
                                                   void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //TODO: actually implement this to enable tofications
    FBUCMembers *members = get_fbuc_members(target);
    uint64_t cb = arguments->scalarInput[0];
    uint64_t ref = arguments->scalarInput[1];
    uint64_t type = arguments->scalarInput[2];
    IOUserClient_setAsyncReference64(&members->notif_ports[type].asnyc_ref64[0],
                                     members->notif_ports[type].port,
                                     cb, ref, members->task);
    return 0;
}

static uint64_t fbuc_ext_meth_change_frame_info(void *target,
                                                void *reference,
                                          IOExternalMethodArguments *arguments)
{
    //TODO: actually implement this
    FBUCMembers *members = get_fbuc_members(target);

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


    if ((selector >= FBUC_MAX_EXT_FUNCS) ||
        (0 == members->fbuc_external_methods[selector].function)) {
        cancel();
    }
    new_dispatch = &members->fbuc_external_methods[selector];
    return IOUserClient_externalMethod(this, selector, args, new_dispatch,
                                       this, reference);
}

uint64_t fbuc_clientClose(void *this)
{
    void **vtable_ptr = (void **)*(uint64_t *)this;
    FuncIOSerivceTerminate vfunc_terminate =
        (FuncIOSerivceTerminate)vtable_ptr[IOSERVICE_TERMINATE_INDEX];
    vfunc_terminate(this, 0);
    return 0;
}

uint64_t fbuc_connectClient(void *this, void *user_client)
{
    cancel();
    return 0;
}

uint64_t fbuc_getNotificationSemaphore(void *this, uint64_t type, void *sem)
{
    cancel();
    return 0;
}

uint64_t fbuc_clientMemoryForType(void *this, uint64_t type, void *opts,
                                  void **mem)
{
    cancel();
    return 0;
}

uint64_t fbuc_registerNotificationPort(void *this, void *port,
                                       uint64_t type, uint64_t ref)
{
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
    FBUCMembers *members = get_fbuc_members(this);
    members->task = task;
    return IOUserClient_initWithTask(this, task, sid, type);
}

uint64_t fbuc_destructor(void *this)
{
    void *obj = IOUserClient_destructor(this);
    OSObject_delete(obj, ALEPH_FBUC_SIZE);
    return 0;
}
