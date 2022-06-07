#ifndef OPT_H
#define OPT_H

#define OPT_SECTION cli_options
#define OPT_BEG_SECTION CAT(__start_, OPT_SECTION)
#define OPT_END_SECTION CAT(__stop_, OPT_SECTION)

/*
 * Forcing correct alignement of the 'struct opt' put into the
 * OPT_SECTION.  Otherwise, the iterator won't work because the linker
 * will go haywire.
 */
#if __x86_64__ || __aarch64__ || __powerpc64__ || __sparc__ || __mips__
#  define OPT_STRUCT_ALIGN 8
#elif __i386__ || __arm__ || __m68k__ || __ILP32__
#  define OPT_STRUCT_ALIGN 4
#endif

enum opt_type {
	OPT_FLG,
	OPT_INT,
	OPT_STR,
	OPT_CLB
};

struct opt {
	int type;
	const char *name;
	const char *help;
	union {
		bool *flg;
		int  *num;
		const char **str;
		void (*clb)(void);
	};
};

extern int opt_parse(int argc, char **argv, struct opt *options, usize len);
extern void opt_usage(const char *usage, struct opt *options, usize len);

#define OPT_GENERIC_MAKE(TYPE, NAME, HELP, VAL, MEMBER)			\
	static struct opt MAKE_ID(opt_)					\
		__section(STR(OPT_SECTION))				\
		__used							\
		__align(OPT_STRUCT_ALIGN) = {				\
		.type	 = TYPE,					\
		.name	 = NAME,					\
		.help	 = HELP,					\
		.MEMBER	 = VAL						\
	}

#define OPT_MAKE_FLG(NAME, HELP, VAL)		\
	OPT_GENERIC_MAKE(OPT_FLG, NAME, HELP, VAL, flg)

#define OPT_MAKE_INT(NAME, HELP, VAL)		\
	OPT_GENERIC_MAKE(OPT_INT, NAME, HELP, VAL, num)

#define OPT_MAKE_STR(NAME, HELP, VAL)		\
	OPT_GENERIC_MAKE(OPT_STR, NAME, HELP, VAL, str)

#define OPT_MAKE_CLB(NAME, HELP, VAL)		\
	OPT_GENERIC_MAKE(OPT_CLB, NAME, HELP, VAL, clb)

#endif
