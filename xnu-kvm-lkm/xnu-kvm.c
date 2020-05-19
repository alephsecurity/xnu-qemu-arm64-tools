#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include "xnu-kvm.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Lev Aronsky");
MODULE_DESCRIPTION("A Linux module that changes KVM behaviour.");
MODULE_VERSION("0.03");

void **arm_exit_handlers;
kvm_arm_handler_fn kvm_handle_sys_reg_orig, kvm_handle_hvc_orig;

static uint64_t custom_cpregs[12] = {0};

/*
 * Return 0 (and set exit reason) for proper exit to user-space.
 */
int kvm_handle_hvc_hook(struct kvm_vcpu *vcpu, struct kvm_run *run) {
  u32 hvc_imm = kvm_vcpu_hvc_get_imm(vcpu);
  u64 hvc_x0  = vcpu_get_reg(vcpu, 0);

  printk(KERN_INFO "KVM Enhancements: hvc #%x [x0 = %llx] called!\n", hvc_imm, hvc_x0);

  if (hvc_imm) {
    run->exit_reason = KVM_EXIT_HYPERCALL;
    run->hypercall.nr = hvc_imm;
    run->hypercall.args[0] = vcpu_get_reg(vcpu, 0);
    run->hypercall.args[1] = vcpu_get_reg(vcpu, 1);
    run->hypercall.args[2] = vcpu_get_reg(vcpu, 2);
    run->hypercall.args[3] = vcpu_get_reg(vcpu, 3);
    run->hypercall.args[4] = vcpu_get_reg(vcpu, 4);
    run->hypercall.args[0] = vcpu_get_reg(vcpu, 5);

    return 0;
  }

  return kvm_handle_hvc_orig(vcpu, run);
}

/*
 * Return 0 (and set exit reason) for proper exit to user-space.
 */
int kvm_handle_sys_reg_hook(struct kvm_vcpu *vcpu, struct kvm_run *run) {
  struct sys_reg_params params;
  unsigned long esr = kvm_vcpu_get_hsr(vcpu);
  int Rt = kvm_vcpu_sys_get_rt(vcpu);
  uint64_t *storage;

  params.is_aarch32 = false;
  params.is_32bit = false;
  params.Op0 = (esr >> 20) & 3;
  params.Op1 = (esr >> 14) & 0x7;
  params.CRn = (esr >> 10) & 0xf;
  params.CRm = (esr >> 1) & 0xf;
  params.Op2 = (esr >> 17) & 0x7;
  params.regval = vcpu_get_reg(vcpu, Rt);
  params.is_write = !(esr & 1);

  if ((params.Op0 == 3) && (params.CRn == 15)) {
    switch (params.Op1) {
    case 0:
      if (params.CRm == 3) {
        storage = &custom_cpregs[0];
      }
      else if (params.CRm == 4) {
        storage = &custom_cpregs[1];
      }
      else if (params.CRm == 5) {
        storage = &custom_cpregs[2];
      }
      else if (params.CRm == 7) {
        storage = &custom_cpregs[3];
      }
      else if (params.CRm == 8) {
        storage = &custom_cpregs[4];
      }
      else if (params.CRm == 13) {
        storage = &custom_cpregs[5];
      }
      else goto kvm_impl;
      break;
    case 1:
      if (params.CRm == 0) {
        storage = &custom_cpregs[6];
      }
      else if (params.CRm == 1) {
        storage = &custom_cpregs[7];
      }
      else if (params.CRm == 13) {
        storage = &custom_cpregs[8];
      }
      else goto kvm_impl;
      break;
    case 2:
      if (params.CRm == 0) {
        storage = &custom_cpregs[9];
      }
      else if (params.CRm == 1) {
        storage = &custom_cpregs[10];
      }
      else goto kvm_impl;
      break;
    case 3:
      if (params.CRm == 0) {
        storage = &custom_cpregs[11];
      }
      else goto kvm_impl;
      break;
    default:
      goto kvm_impl;
    }
  } else goto kvm_impl;

  if (!params.is_write) {
    vcpu_set_reg(vcpu, Rt, *storage);
  } else {
    *storage = params.regval;
  }

  *vcpu_pc(vcpu) += 4;
  *vcpu_cpsr(vcpu) &= ~DBG_SPSR_SS;

  return 1;

kvm_impl:
  return kvm_handle_sys_reg_orig(vcpu, run);
}

int disable_protection(uint64_t addr) {
  /* Manually disable write-protection of the relevant page.
     Taken from:
       https://stackoverflow.com/questions/45216054/arm64-linux-memory-write-protection-wont-disable
  */
  pgd_t *pgd;
  pte_t *ptep, pte;
  pud_t *pud;
  pmd_t *pmd;

  pgd = pgd_offset((struct mm_struct*)kallsyms_lookup_name("init_mm"), (addr));

  if (pgd_none(*pgd) || pgd_bad(*pgd))
    goto out;
  printk(KERN_NOTICE "Valid pgd 0x%px\n",pgd);

  pud = pud_offset(pgd, addr);
  if (pud_none(*pud) || pud_bad(*pud))
    goto out;
  printk(KERN_NOTICE "Valid pud 0x%px\n",pud);

  pmd = pmd_offset(pud, addr);
  if (pmd_none(*pmd) || pmd_bad(*pmd))
    goto out;
  printk(KERN_NOTICE "Valid pmd 0x%px\n",pmd);

  ptep = pte_offset_map(pmd, addr);
  if (!ptep)
    goto out;
  pte = *ptep;

  printk(KERN_INFO "PTE before 0x%lx\n", *(unsigned long*) &pte);
  printk(KERN_INFO "Setting PTE write\n");

  pte = pte_mkwrite(pte);
  *ptep = clear_pte_bit(pte, __pgprot((_AT(pteval_t, 1) << 7)));

  printk(KERN_INFO "PTE after         0x%lx\n", *(unsigned long*) &pte);
  flush_tlb_all();
  printk(KERN_INFO "PTE nach flush    0x%lx\n", *(unsigned long*) &pte);

  return 0;

out:
  return 1;
}

static int __init kvm_enhancer_init(void) {
  arm_exit_handlers = (void**) kallsyms_lookup_name("arm_exit_handlers");
  if (NULL == arm_exit_handlers) {
    printk(KERN_ERR "KVM Enhancements: arm_exit_handlers not found, make sure you're using a supported kernel!\n");
    return 1;
  }

  kvm_handle_sys_reg_orig = arm_exit_handlers[ESR_ELx_EC_SYS64];
  kvm_handle_hvc_orig     = arm_exit_handlers[ESR_ELx_EC_HVC64];

  printk(KERN_INFO "KVM Enhancements: kvm_handle_sys_reg @ 0x%px\n", kvm_handle_sys_reg_orig);
  printk(KERN_INFO "KVM Enhancements: kvm_handle_hvc     @ 0x%px\n", kvm_handle_hvc_orig);
  printk(KERN_INFO "KVM Enhancements: setting hooks...\n");

  if (disable_protection((uint64_t) arm_exit_handlers)) {
    printk(KERN_ERR "KVM Enhancements: Couldn't disable write protection on arm_exit_handlers!\n");
    return 2;
  }

  arm_exit_handlers[ESR_ELx_EC_SYS64] = kvm_handle_sys_reg_hook;
  arm_exit_handlers[ESR_ELx_EC_HVC64] = kvm_handle_hvc_hook;

  printk(KERN_INFO "KVM Enhancements: hooks set!\n");
  printk(KERN_INFO "KVM Enhancements: loaded!\n");
  return 0;
}

static void __exit kvm_enhancer_exit(void) {
  printk(KERN_INFO "KVM Enhancements: removing hooks...\n");

  arm_exit_handlers[ESR_ELx_EC_SYS64] = kvm_handle_sys_reg_orig;
  arm_exit_handlers[ESR_ELx_EC_HVC64] = kvm_handle_hvc_orig;

  printk(KERN_INFO "KVM Enhancements: hook removed!\n");
  printk(KERN_INFO "KVM Enhancements: unloaded!\n");
}

module_init(kvm_enhancer_init);
module_exit(kvm_enhancer_exit);
