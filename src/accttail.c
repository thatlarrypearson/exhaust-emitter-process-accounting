/* accttail.c
**
** Description:
**	Reads Linux process accounting file and sends string/text records to standard output.
**	In a way, this program "tails" the accounting file.
**
**	The program will reopen (log rotation) a file when:
**		kill -SIGHUP <accttail-pid>
**		kill -1 <accttail-pid>
**
** Compile:
**	cc accttail.c -o accttail
**
** Licensing
**
** Licensing
**
** The MIT License (MIT)
**
** Copyright (c) 2015 Lawrence Bennett Pearson
**
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
**
** The above copyright notice and this permission notice shall be included in
** all copies or substantial portions of the Software.
**
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
** SOFTWARE.
*/
#include <sys/acct.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>

static	FILE		*fp = NULL;
static	char		*fname = "/var/log/account/pacct";
static	char		*fmode = "rb";
static	struct	acct_v3	acctVal;
static	char		acctStr[BUFSIZ];
static	int		reOpenFile = 0;

void sighup_handler(int signalNumber)
{
	if( signalNumber == SIGHUP )
	{
		reOpenFile = 1;
	}
}

long	comp_t2long(comp_t c)
{
	return (c & 0x1fff) << (((c >> 13) & 0x7) * 3);
}

char	*acct2str(char *buf, struct acct_v3 *ptr)
{
	int	rtnVal = 0;
	/*
	** http://man7.org/linux/man-pages/man5/acct.5.html
	**
	** int snprintf(char *str, size_t size, const char *format, 
	*/
	rtnVal = snprintf(buf, BUFSIZ, "%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%f,%ld,%ld,%ld,%ld,%ld,%s\n",
				(long) ptr->ac_flag,
				(long) ptr->ac_version,
				(long) ptr->ac_tty,
				(long) ptr->ac_exitcode,
				(long) ptr->ac_uid,
				(long) ptr->ac_gid,
				(long) ptr->ac_pid,
				(long) ptr->ac_ppid,
				(long) ptr->ac_btime,
				ptr->ac_etime,
				comp_t2long(ptr->ac_utime)/sysconf(_SC_CLK_TCK),
				comp_t2long(ptr->ac_stime)/sysconf(_SC_CLK_TCK),
				comp_t2long(ptr->ac_mem),
				comp_t2long(ptr->ac_minflt),
				comp_t2long(ptr->ac_majflt),
				ptr->ac_comm
			);
	return buf;
}


int main(int argc, char *argv[])
{
	int	forever = 1;
	long	cnt = 0;
	char	*s;
	char	buf[BUFSIZ];

	if( signal(SIGHUP, sighup_handler) == SIG_ERR )
	{
		(void) snprintf(buf, BUFSIZ, "Failed to catch SIGHUP\n");
		perror(buf);
		exit(1);
	}

	while( forever )
	{
		if( (fp = fopen(fname, fmode)) == NULL )
		{
			(void) snprintf(buf, BUFSIZ, "Failed to fopen(<%s>,<%s>)\n", fname, fmode);
			perror(buf);
			exit(1);
		}
		while( fp )
		{
			if( (cnt = fread(&acctVal, 1, sizeof(struct acct_v3), fp)) != sizeof(struct acct_v3) )
			{
				clearerr(fp);
				(void) sleep(1);
			}
			else
			{
				s = acct2str(acctStr, &acctVal);
				printf("%s", s);
				fflush(stdout);
			}
			
			if( reOpenFile )
			{
				fclose(fp);
				fp = NULL;
				reOpenFile = 0;
				break;
			}
		}
	}
	exit(0);
}
