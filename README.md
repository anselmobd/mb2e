# mb2e

Create EML files from mails in a Thunderbird MBOX file in a subdirectory.

Version 0.1.6 2017-06-28 (C) Anselmo Blanco Dominguez (Oxigenai)

Tested in only one environment, with this característics:
- Ubuntu 16.04
- Python 3.5.2
- MBOX files from Thunderbird 45.8.0
- Thunderbird, files and script in the same machine
- before and after running "Condense Folder" routine from Thunderbird

Usage: mb2e.py path/to/mbox

Funcionality
The script:
- Create a directorie with the name of the MBOX file appended with '.__mb2e__'
- For each mail encountred in the file the script get the Message-ID
- Each mail is saved in the created directorie with the name "Message-ID".eml

To do:
- clean and enhance the code quality
- test in other environments
- better logger
- treat the second extraction of emails, such as archiving deleted emails and
   not rewriting equal emails.
- detect bad e-mails and bad attachments
- save separated header and body

Future related projects:
- Extract attachments to subdirectory
- Extract all parts

Obs.: The complexity of the script stems from the fact that it creates a
small check if the default EMLs tab within MBOX is valid. As far as I can
tell, Thuderbird himself takes care of this, but I think it's best not to
assume that everything is ok.

-- History

Version 0.1.6 2017-06-28
. More parameter: lineLimit
. All inside the class

Version 0.1.5 2017-06-28
. Starting gettext
. Using argparse
. Usinf VerboseOutput

Version 0.1.4 2017-06-27
. No dolar in eml name

Version 0.1.3 2017-06-27
. Clean Mozilla tags
. remove old code

Version 0.1.2 2017-06-27
. Rewrite using class
. Bug in detecting message id
. Logger
. Evolving
. Mantein old code for comparison

Version 0.1.1 2017-06-26
. Much mo more tests (same plataform)
. Sane "eml" file name
. Evolving header regex

Version 0.1 2017-04-11 (C) Anselmo Blanco Dominguez (Oxigenai)
. First version
