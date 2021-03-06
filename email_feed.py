#!/usr/bin/env python3
import sys
import os
import time
import traceback
from argparse import ArgumentParser
import imaplib
import email
from email.header import decode_header
import hashlib
import cfgreader
import logging
import html
from typing import Callable, List, Tuple

# Read in custom configurations
g_cfg = cfgreader.CfgReader(__file__.replace('.py', '.cfg'))

# These two strings will form the header and individual
# items of the RSS feed.
feed_header = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Emails for %s</title>
<link>%s</link>
<atom:link href="http://%s/%s.xml" rel="self" type="application/rss+xml" />
<pubDate>%%s</pubDate>
<description>Feed automatically generated by %s's %s</description>
<language>en-us</language>
""" % (g_cfg.main.name, g_cfg.imap.webmail, g_cfg.main.url_base,
       g_cfg.main.rss_base, g_cfg.main.url_base, os.path.basename(__file__))

feed_item = """<item>
<title>%s</title>
<pubDate>%s</pubDate>
<link>%s</link>
<guid isPermaLink="false">%s</guid>
<description>"%s" sent on %s</description>
</item>
"""


v_print:Callable
def set_v_print(verbose: bool) -> None:
    """
    Defines the function v_print.
    It prints if verbose is true, otherwise, it does nothing.
    See: http://stackoverflow.com/questions/5980042
    :param verbose: A bool to determine if v_print will print its args.
    """
    global v_print
    v_print = print if verbose else lambda *a, **k: None


def write_feed(feed_dir: str, feed_items: List[Tuple[str, str, str]]) -> str:
    """ Given a list of feed_items, write an FSS feed. """
    now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    do_move = False
    temp_fname = os.path.join(feed_dir, g_cfg.main.rss_base + '.temp.xml')
    dest_fname = os.path.join(feed_dir, g_cfg.main.rss_base + '.xml')
    with open(temp_fname, 'w', encoding='utf-8') as f:
        f.write(feed_header % (now,))
        for title, url, sent_date in reversed(feed_items):
            title = html.escape(title)
            guid = hashlib.sha1(bytes(title + sent_date, 'utf-8')).hexdigest()
            f.write(feed_item % (title,
                                 sent_date,
                                 url,
                                 guid,
                                 title, sent_date[:-15]))
        f.write('</channel></rss>')
        do_move = True
    if do_move:
        os.rename(temp_fname, dest_fname)
        return "OK (You got %d new message%s.)" % \
               (len(feed_items), len(feed_items) > 1 and "s" or "")
    return "Could not update the feed file."


def main(feed_dir: str) -> None:
    """ Fetch all the unread mail, and make a feed of subject lines.
    """
    start_time = time.time()
    server = imaplib.IMAP4_SSL(g_cfg.imap.mailbox)
    server.login(g_cfg.imap.user, g_cfg.imap.password)
    server.select()
    status, data = server.search(None, '(UNSEEN)')
    if status != 'OK':
        raise Exception('Getting the list of messages resulted in %s' % status)

    feed_items = []
    logging.debug("There are %d UNSEEN items." % len(data[0].split()))
    for num in data[0].split():  # For each email message...
        status, data = server.fetch(num, '(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE FROM)])')
        if status != 'OK':
            raise Exception('Fetching message %s resulted in %s' % (num, status))
        logging.debug("Fetched message %s." % num)
        msg = email.message_from_bytes(data[0][1])
        subject = msg['Subject']
        from_addr = msg['From']
        logging.debug("    Subject: %s" % subject)
        logging.debug("    From: %s" % from_addr)
        logging.debug("    Date: %s" % msg['Date'])
        codec = 'utf-8'
        if subject.startswith('=?'):
            subject, codec = decode_header(subject)[0]
        if not isinstance(subject, str):
            subject = subject.decode(codec)

        # Append the subject to a list of items
        feed_items.append((subject, g_cfg.imap.webmail, msg['Date']))

    # Ensure the new feed is written
    update_status = "OK"
    if len(feed_items) > 0:
        update_status = write_feed(feed_dir, feed_items)

    server.close()
    server.logout()
    logging.info("%2.0fs %s" % (time.time() - start_time, update_status))
    v_print(update_status)


if __name__ == '__main__':
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    logging.basicConfig(filename=os.path.join(script_dir, g_cfg.main.logfile),
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging.INFO)
    web_dir = '/var/www/html'
    parser = ArgumentParser(description="cronjob to check for email.")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    set_v_print(args.verbose)
    v_print("Log at %s" % os.path.join(script_dir, g_cfg.main.logfile))

    try:
        main(web_dir)
    except Exception as e:
        exceptional_text = "Exception: " + str(e.__class__) + " " + str(e)
        logging.critical(exceptional_text)
        logging.critical(traceback.format_exc())
        print(exceptional_text)
        traceback.print_exc(file=sys.stdout)
