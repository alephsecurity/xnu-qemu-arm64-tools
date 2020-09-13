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

#ifndef KERN_FUNCS_H
#define KERN_FUNCS_H

enum IODirection
{
    kIODirectionNone  = 0x0,//                    same as VM_PROT_NONE
    kIODirectionIn    = 0x1,// User land 'read',  same as VM_PROT_READ
    kIODirectionOut   = 0x2,// User land 'write', same as VM_PROT_WRITE
};

#define IOBLOCKSTORAGEDEVICE_MCLASS_INST_PTR (0xfffffff0076f6e58)
#define IOBLOCKSTORAGEDEVICE_MCLASS_VTABLE_PTR (0xfffffff006e14200)
#define IOBLOCKSTORAGEDEVICE_VTABLE_PTR (0xfffffff006e13c00)
#define IOBLOCKSTORAGEDEVICE_CONSTRUCTOR_FUNC_PTR (0xfffffff00619ad80)

#define IOMFB_MCLASS_INST_PTR (0xfffffff00771b408)
#define IOMFB_MCLASS_VTABLE_PTR (0xfffffff006e8d4b8)
#define IOMFB_VTABLE_PTR (0xfffffff006e8ca10)
#define IOMFB_CONSTRUCTOR_FUNC_PTR (0xfffffff00636a660)

#define IOSERVICE_MCLASS_INST_PTR (0xfffffff007602b68)
#define IOSERVICE_MCLASS_VTABLE_PTR (0xfffffff007086e80)
#define IOSERVICE_VTABLE_PTR (0xfffffff007086300)

#define IOUC_MCLASS_INST_PTR (0xfffffff0076033f8)
#define IOUC_MCLASS_VTABLE_PTR (0xfffffff007091058)
#define IOUC_VTABLE_PTR (0xfffffff007090a78)

#define SALLCLASSESDICT_PTR (0xfffffff007672e00)
#define SALLCLASSESLOCK_PTR (0xfffffff007672dc0)
#define SSTALLEDCLASSESLOCK_PTR (0xfffffff007672dd0)

//OSMetaClass::instanceConstructed() const
void _ZNK11OSMetaClass19instanceConstructedEv(void *meta_class_inst_ptr);
#define OSMetaClass_instanceConstructed(x) \
        _ZNK11OSMetaClass19instanceConstructedEv(x)

//OSMetaClass::allocClassWithName(char const*)
void *_ZN11OSMetaClass18allocClassWithNameEPKc(char *name);
#define OSMetaClass_allocClassWithName(x) \
        _ZN11OSMetaClass18allocClassWithNameEPKc(x)

//OSObject::operator new(unsigned long)
void *_ZN8OSObjectnwEm(uint64_t size);
#define OSObject_new(x) _ZN8OSObjectnwEm(x)

//OSMetaClass::OSMetaClass(char const*, OSMetaClass const*, unsigned int)
void *_ZN11OSMetaClassC2EPKcPKS_j(void *meta_class_inst_ptr, char *class_name,
                                  void *parent_meta_class_inst_ptr,
                                  uint64_t size);
#define OSMetaClass_OSMetaClass(w, x, y, z) \
        _ZN11OSMetaClassC2EPKcPKS_j(w, x, y, z)

//OSSymbol::withCStringNoCopy(char const*)
void *_ZN8OSSymbol17withCStringNoCopyEPKc(char *str);
#define OSSymbol_withCStringNoCopy(x) _ZN8OSSymbol17withCStringNoCopyEPKc(x)

//OSDictionary::setObject(OSSymbol const*, OSMetaClassBase const*)
void _ZN12OSDictionary9setObjectEPK8OSSymbolPK15OSMetaClassBase(void *dict,
                                                                void *sym,
                                                                void *obj);
#define OSDictionary_setObject(x, y, z) \
        _ZN12OSDictionary9setObjectEPK8OSSymbolPK15OSMetaClassBase(x, y, z)

//IOService::serviceMatching(char const*, OSDictionary*)
void *_ZN9IOService15serviceMatchingEPKcP12OSDictionary(char *class_name,
                                                        void *dict);
#define IOService_serviceMatching(x, y) \
        _ZN9IOService15serviceMatchingEPKcP12OSDictionary(x, y)

//IOService::nameMatching(char const*, OSDictionary*)
void *_ZN9IOService12nameMatchingEPKcP12OSDictionary(char *name,
                                                     void *dict);
#define IOService_nameMatching(x, y) \
        _ZN9IOService12nameMatchingEPKcP12OSDictionary(x, y)

//OSDictionary * waitForMatchingService(OSDictionary *param_1,long_long param_2)
void *_ZN9IOService22waitForMatchingServiceEP12OSDictionaryy(void *dict,
                                                             uint64_t timeout);
#define waitForMatchingService(x, y) \
        _ZN9IOService22waitForMatchingServiceEP12OSDictionaryy(x, y)

//IOService::IOService(OSMetaClass*)
void _ZN9IOServiceC1EPK11OSMetaClass(void *this, void *metaclass);
#define IOService_IOService(x, y) _ZN9IOServiceC1EPK11OSMetaClass(x, y)

//IOService::start(IOService*)
uint64_t _ZN9IOService5startEPS_(void *this);
#define IOService_start(x) _ZN9IOService5startEPS_(x)

//IOUserClient::IOUserClient(OSMetaClass const*
void _ZN12IOUserClientC2EPK11OSMetaClass(void *this, void *metaclass);
#define IOUserClient_IOUserClient(x, y) \
        _ZN12IOUserClientC2EPK11OSMetaClass(x, y)

//IOUserClient::externalMethod
uint64_t
_ZN12IOUserClient14externalMethodEjP25IOExternalMethodArgumentsP24IOExternalMethodDispatchP8OSObjectPv(
                            void *this, uint32_t selector, void *args,
                            void *dispatch, void *target, void *reference);
#define IOUserClient_externalMethod(a, b, c, d, e, f) \
        _ZN12IOUserClient14externalMethodEjP25IOExternalMethodArgumentsP24IOExternalMethodDispatchP8OSObjectPv(a, b, c, d, e, f)

//IOUserClient::~IOUserClient()
void *_ZN12IOUserClientD2Ev(void *this);
#define IOUserClient_destructor(x) _ZN12IOUserClientD2Ev(x)

//OSObject::operator delete(void*, unsigned long
void _ZN8OSObjectdlEPvm(void *obj, uint64_t size);
#define OSObject_delete(x, y) _ZN8OSObjectdlEPvm(x, y)

//IOUserClient::initWithTask(task*, void*, unsigned int)
uint64_t _ZN12IOUserClient12initWithTaskEP4taskPvj(void *this, void *task,
                                                   void *sid, uint64_t type);
#define IOUserClient_initWithTask(a, b, c, d) \
    _ZN12IOUserClient12initWithTaskEP4taskPvj(a, b, c, d)

//IOUserClient::setAsyncReference64(unsigned long long*, ipc_port*, unsigned long long, unsigned, long long, task*)
void _ZN12IOUserClient19setAsyncReference64EPyP8ipc_portyyP4task(void *aref,
                                                                 void *port,
                                                                 uint64_t cb,
                                                                 uint64_t ref,
                                                                 void *task);
#define IOUserClient_setAsyncReference64(a, b, c, d, e) \
    _ZN12IOUserClient19setAsyncReference64EPyP8ipc_portyyP4task(a, b, c, d, e)

//IOUserClient::sendAsyncResult64(unsigned long long*, int, unsigned long long*, unsigned int)
void _ZN12IOUserClient17sendAsyncResult64EPyiS0_j(void *aref, uint64_t res,
                                                  uint64_t *args, uint64_t cnt);
#define IOUserClient_sendAsyncResult64(a, b, c, d) \
    _ZN12IOUserClient17sendAsyncResult64EPyiS0_j(a, b, c, d)

//void _IOLog(undefined8 param_1)
void IOLog(const char* fmt, ...);

//void _IOSleep(undefined8 param_1)
void IOSleep(uint64_t millisecs);

void *current_task();

void lck_mtx_lock(void *lck_mtx);
void lck_mtx_unlock(void *lck_mtx);
void *lck_grp_alloc_init(char *name, void *p2);
void *lck_mtx_alloc_init(void *mtx_grp, void *p2);

void kernel_thread_start(void *code, void *param, void *new_thread);

char *strncat(char *destination, const char *source, size_t size);

void *kern_os_malloc(size_t size);
void kern_os_free(void *buf);

#endif
