get-pdf

Small python programm, which will help you organize pdf files from email in folders on computer.

To login you should have file 'users.json' in current directory with following format:
{
	"accounts": [
		{	
			"name" 		:	"name of account",
			"server"	:	"imap.gmail.com", # for example
			"login"		:	"email login",
			"password" 	:	"email password"
		}
	]
}