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

//OSDictionary * waitForMatchingService(OSDictionary *param_1,long_long param_2)
void *_ZN9IOService22waitForMatchingServiceEP12OSDictionaryy(void *dict,
                                                             uint64_t timeout);
#define waitForMatchingService(x, y) \
        _ZN9IOService22waitForMatchingServiceEP12OSDictionaryy(x, y)

//IOService::attach(IOService*)
uint64_t _ZN9IOService6attachEPS_(void *this, void *parent);
#define IOService_attach(x, y) _ZN9IOService6attachEPS_(x, y)

//void _IOLog(undefined8 param_1)
void IOLog(const char* fmt, ...);

void lck_mtx_lock(void *lck_mtx);
void lck_mtx_unlock(void *lck_mtx);
void *lck_grp_alloc_init(char *name, void *p2);
void *lck_mtx_alloc_init(void *mtx_grp, void *p2);

#endif
