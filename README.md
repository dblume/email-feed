[![Code Climate](https://codeclimate.com/github/dblume/email-feed/badges/gpa.svg)](https://codeclimate.com/github/dblume/email-feed)
[![Issue Count](https://codeclimate.com/github/dblume/email-feed/badges/issue_count.svg)](https://codeclimate.com/github/dblume/email-feed/issues)
[![License](https://img.shields.io/badge/license-MIT_license-blue.svg)](https://raw.githubusercontent.com/dblume/email-feed/master/LICENSE.txt)
![python2.x](https://img.shields.io/badge/python-2.x-yellow.svg)

# email-feed

email-feed is a script that scans email and creates an RSS feed for unread messages. It only shares titles, it doesn't reveal message contents. It should be run as a cronjob.

## Getting Started

1. Rename email\_feed.cfg.sample to email\_feed.cfg
2. Customize the variables in email\_feed.cfg (More on this below.)
3. Set up a cronjob that runs email\_feed every day.
4. Set up something to maintain the size of its log file.

## What It Does

It scans an email account and creates an RSS feed for unread messages. This is useful for any email accounts that you rarely check if you use a feed reader.

For each unread email, it'll create a feed item like so:

    <item>
      <title>
        [CoinBase] Bitcoin transaction complete.
      </title>
      <pubDate>Fri, 16 Nov 2012 07:23:52 +0000 (UTC)</pubDate>
      <link>https://webmail.yourdomain.com/</link>
      <guid isPermaLink="false">7aa13ff7fc1542e3c609aa41fbbc6bc61cb1f4e4</guid>
      <description>
        "[CoinBase] Bitcoin transaction complete." sent on Fri, 16 Nov 2012 07:23
      </description>
    </item>

The logfile it writes looks something like this:

    2012-10-08 13:00  1s OK (Wrote 1 new item.)
    2012-10-09 13:00  0s OK
    2012-10-10 13:00  1s OK (Wrote 3 new items.)
    2012-10-11 13:00  0s OK

The RSS feed it writes validates at [the feed validation service](http://validator.w3.org/appc/).

## Customizing email\_feed.cfg

email\_feed.cfg looks like this:

    [main]
    domain = yourdomain.com
    name = John Doe
    url_base = %(domain)s
    logfile = logfile.log
    rss_base = email_feed
    [imap]
    mailbox = mail.yourdomain.com
    user = email@yourdomain.com
    password = mooltipass

### The Main Section

This section refers to stuff like the name and location of the new RSS file.

**domain**: This is the domain that the script resides at and will write the RSS feed to.  
**name**: The name of the person to whom the NetFlix feed belongs.  
**url\_base**: The base of the URL that the RSS feed is at.  
**logfile**: The name of the logfile.  
**rss\_base**: The base filename of the RSS file.  '.xml' will be appended to the end.

Given the example above, the complete URL for the feed would be `http://yourdomain.com/email_feed.xml`.

### The IMAP Section

This section refers to the mailbox that the script will read to create the feed.

**mailbox**: The internet address of the email mailbox.  
**user**: The user for the email address to which you've forwarded the NetFlix email.  
**password**: The IMAP password.

## Maintaining the size of the logfile

You should use the mechanism provided by your operating system. But if you want to roll your own, something like the following will work:

    find $HOME/log -maxdepth 1 -name \*\.log -type f ! -executable -print0 | \
    xargs -0 -I{} sh -c 'if [ $(wc -l < {}) -gt 100 ]; then TMPF=$(mktemp) && tail -100 {} > $TMPF && mv $TMPF {}; fi'

## Is it any good?

[Yes](https://news.ycombinator.com/item?id=3067434).


## Debugging

Run the command with the ``--verbose`` flag for verbose logging.

## Licence

This software uses the [MIT License](http://opensource.org/licenses/mit-license.php).
