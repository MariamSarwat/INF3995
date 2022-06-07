#ifndef REST_H
#define REST_H

#include "utils/btree.h"
#include "utils/http.h"
#include "utils/json.h"

#define REST_AUTH_GET	 0x1u
#define REST_AUTH_PUT	 0x2u
#define REST_AUTH_POST	 0x4u
#define REST_AUTH_DELETE 0x4u
#define REST_AUTH_ALL	 (REST_AUTH_GET | REST_AUTH_PUT | REST_AUTH_POST | REST_AUTH_DELETE)

struct rest_interface {
	const char *route;
	enum http_status (*get)	  (const char *user, const struct json *request, struct json **response);
	enum http_status (*put)	  (const char *user, const struct json *request, struct json **response);
	enum http_status (*post)  (const char *user, const struct json *request, struct json **response);
	enum http_status (*delete)(const char *user, const struct json *request, struct json **response);
	struct btree node;
	u32 options;
};

extern void rest_register(struct rest_interface *interface);
extern void rest_handle(FILE *rd, FILE *fp);

/*
 * Forcing correct alignement of the 'struct rest_interface' put into
 * the REST_INTERFACE_SECTION.	Otherwise, the iterator won't work
 * because the linker will go haywire.
 */
#if __x86_64__ || __aarch64__ || __powerpc64__ || __sparc__ || __mips__
#  define REST_STRUCT_INTERFACE_ALIGN 8
#elif __i386__ || __arm__ || __m68k__ || __ILP32__
#  define REST_STRUCT_INTERFACE_ALIGN 4
#endif

#define REST_INTERFACE_SECTION rest_interface_section
#define REST_INTERFACE_BEG     CAT(__start_, REST_INTERFACE_SECTION)
#define REST_INTERFACE_END     CAT(__stop_, REST_INTERFACE_SECTION)

#define REST_MAKE_URI						\
	static struct rest_interface MAKE_ID(rest_interface)	\
		__section(STR(REST_INTERFACE_SECTION))		\
		__align(REST_STRUCT_INTERFACE_ALIGN)		\
		__used


#define REST_REGISTER_LIB						\
	__ctor								\
	static void rest_register_lib_ctor(void)			\
	{								\
		extern struct rest_interface REST_INTERFACE_BEG;	\
		extern struct rest_interface REST_INTERFACE_END;	\
									\
		for (struct rest_interface *it=&REST_INTERFACE_BEG;	\
		     it<&REST_INTERFACE_END; ++it) {			\
			rest_register(it);				\
		}							\
									\
	}								\
	_Static_assert(true, "")

#endif
