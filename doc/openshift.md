## Accessing the COTwins server on Openshift.

The COTwins server is currently running on Openshift.

To access, first you need an Openshift account, and I need to add you to the project,
which is called "assesment".

Log into openshift.

### SSH Keys
First you need to configure your account to have the right access keys ("SSH keys") in order to be granted access.

First you need to generate an SSH key. Follow these directions:
https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/

Assuming you have a mac, you want to now copy your SSH key to the clipboard.:

    clip < ~/.ssh/id_rsa.pub

In the Openshift Console Online, click on "Settings". Under "Public Keys" click on  "Add new key..."
Give it a name and paste the contents of your clipboard into the second box.

Now you should be able to access the server.

### Logging into the server
In the Openshift console, and click on "Applications". You should see one called
"assesment" under "cotwins". Click on it. On the right you should see a section with a
command to access the source code. Click on "Want to log into your application".

It will give you a command such as:

    ssh 3434lskddjfklsdjf@assesment-cotwins.rhcloud.com

Copy the command and paste this into a terminal. This should log you onto the LIVE production server.
Be *very* careful.


#### Accessing the database
To access the database, type in `psql`. Again, be very careful as this is the LIVE version of the database.

First connect to the database:

    \c assesment

Now you can run SQL commands to get any data you want:

For example, to get the sessions associated with a user:

    select * from session where token = 'ext4c3maqq93o4e' ORDER BY 1;

If you actually wanted to see the data for a particular task:

    select * from keep_track where token = 'ext4c3maqq93o4e' ORDER BY 1;
