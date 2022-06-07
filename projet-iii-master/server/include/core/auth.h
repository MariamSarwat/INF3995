#ifndef CORE_AUTH_H
#define CORE_AUTH_H

extern void auth_init(void);
extern bool auth_authenticate(const char *restrict user, const char *restrict passwd) __notnull;
extern int  auth_change(const char *restrict user, const char *restrict new_passwd) __notnull;

#endif
