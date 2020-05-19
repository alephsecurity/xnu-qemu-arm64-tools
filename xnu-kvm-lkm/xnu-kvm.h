#ifndef _VCPU_ACCESSORS_H_
#define _VCPU_ACCESSORS_H_

#include <linux/kvm_host.h>

struct sys_reg_params {
        u8      Op0;
        u8      Op1;
        u8      CRn;
        u8      CRm;
        u8      Op2;
        u64     regval;
        bool    is_write;
        bool    is_aarch32;
        bool    is_32bit;       /* Only valid if is_aarch32 is true */
};

typedef int (*kvm_arm_handler_fn)(struct kvm_vcpu*, struct kvm_run*);

static inline unsigned long vcpu_get_reg(const struct kvm_vcpu *vcpu,
                                         u8 reg_num)
{
        return (reg_num == 31) ? 0 : vcpu_gp_regs(vcpu)->regs.regs[reg_num];
}

static inline void vcpu_set_reg(struct kvm_vcpu *vcpu, u8 reg_num,
                                unsigned long val)
{
        if (reg_num != 31)
                vcpu_gp_regs(vcpu)->regs.regs[reg_num] = val;
}

static inline unsigned long *vcpu_pc(const struct kvm_vcpu *vcpu)
{
        return (unsigned long *)&vcpu_gp_regs(vcpu)->regs.pc;
}

static inline unsigned long *vcpu_cpsr(const struct kvm_vcpu *vcpu)
{
        return (unsigned long *)&vcpu_gp_regs(vcpu)->regs.pstate;
}

static inline u32 kvm_vcpu_get_hsr(const struct kvm_vcpu *vcpu)
{
        return vcpu->arch.fault.esr_el2;
}

static inline int kvm_vcpu_sys_get_rt(struct kvm_vcpu *vcpu)
{
        u32 esr = kvm_vcpu_get_hsr(vcpu);
        return ESR_ELx_SYS64_ISS_RT(esr);
}

static inline u32 kvm_vcpu_hvc_get_imm(const struct kvm_vcpu *vcpu)
{
	return kvm_vcpu_get_hsr(vcpu) & ESR_ELx_xVC_IMM_MASK;
}

#endif /* _VCPU_ACCESSORS_H_ */
