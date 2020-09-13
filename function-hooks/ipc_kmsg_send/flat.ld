PHDRS
{
  text PT_LOAD;
}

ENTRY(_start)

SECTIONS
{
  /* Kernel functions */
  INCLUDE kernel.ld

  .start : { *(.start) } :text
  .text : { *(.text) }
}