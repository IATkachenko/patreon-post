import logging
import typing
import sys
import os
from github import Github, Repository
import requests
import json
import markdown


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

_LOGGER.info("Starting")


exit_code: int = 0
post_url: typing.Union[str, None] = None
tag: str = remove_prefix(os.environ.get('GITHUB_REF'), 'refs/tags/')
repo: str = os.environ.get('GITHUB_REPOSITORY')
patreon_login: str = sys.argv[1]
patreon_password: str = sys.argv[2]
post_body: str = sys.argv[3]
release_url: str = "%s/%s/releases/tag/%s" % (os.environ.get('GITHUB_SERVER_URL'), repo, tag)
header: str = 'New release in %s' % repo

should_generate_body: bool = True if post_body == '' else False

if should_generate_body:
    body: str = '###New release in [%s](%s)\n' % (repo, release_url)
    g = Github(base_url=os.environ.get('GITHUB_API_URL'))
    repository: Repository = g.get_repo(repo)
    body += repository.get_release(tag).body
else:
    body = post_body

_LOGGER.debug('Going to create post "%s"', header)

session = requests.Session()

session.cookies.set('patreon_device_id', os.environ.get('PATREON_DEVICE_ID'))

session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
                        'Content-Type': 'application/vnd.api+json'
                        })

response = session.post('https://www.patreon.com/api/login?include=campaign%2Cuser_location&json-api-version=1.0', json={
    "data": {"type": "user", "attributes": {"email": patreon_login, "password": patreon_password},
             "relationships": {}}})
_LOGGER.info("Device is is %s", session.cookies.get('patreon_device_id'))
try:
    csrf_token = json.loads(response.content)['meta']['csrf_token']
except KeyError:
    _LOGGER.critical("csrf token not found in repose")
    _LOGGER.critical("Response is %s", response.content)
    exit(1)

session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
                        'Content-Type': 'application/vnd.api+json',
                        'X-CSRF-Signature': csrf_token
                        })
# get post id
response = json.loads(session.post(
    'https://www.patreon.com/api/posts?fields[post]=post_type%2Cpost_metadata&json-api-version=1.0&include=[]',
    json={"data": {"type": "post", "attributes": {"post_type": "text_only"}}}).content)
#  {
#    "data":{
#      "attributes":{
#        "post_metadata":null,
#        "post_type":"text_only"
#      },
#      "id":"47540764","type":"post"},"links":{"self":"https://www.patreon.com/api/posts/47540764"}}

post_id = response['data']['id']

_LOGGER.debug("New post id is %s", post_id)

# create post
result = session.post(
    'https://www.patreon.com/api/posts/' + post_id + '?include=access_rules.tier.null%2Cattachments.null%2Ccampaign.access_rules.tier.null%2Ccampaign.earnings_visibility%2Ccampaign.is_nsfw%2Cpoll%2Cuser.null%2Cuser_defined_tags.null%2Cimages.null%2Caudio.null&fields[post]=category%2Ccents_pledged_at_creation%2Cchange_visibility_at%2Ccomment_count%2Ccontent%2Ccreated_at%2Ccurrent_user_can_delete%2Ccurrent_user_can_view%2Ccurrent_user_has_liked%2Cdeleted_at%2Cedit_url%2Cedited_at%2Cembed%2Cimage%2Cis_automated_monthly_charge%2Cis_paid%2Clike_count%2Cmin_cents_pledged_to_view%2Cnum_pushable_users%2Cpatreon_url%2Cpatron_count%2Cpledge_url%2Cpost_file%2Cpost_metadata%2Cpost_type%2Cpublished_at%2Cscheduled_for%2Cteaser_text%2Cthumbnail%2Cthumbnail_position%2Ctitle%2Curl%2Cwas_posted_by_campaign_owner%2Cvideo_external_upload_url&fields[access_rule]=access_rule_type%2Camount_cents&fields[reward]=title%2Camount_cents%2Ccurrency%2Cpatron_count%2Cid%2Cpublished&fields[campaign]=is_nsfw&fields[media]=id%2Cimage_urls%2Cdownload_url%2Cmetadata&json-api-version=1.0',
    json={
        "data": {
            "type": "post",
            "attributes": {
                "content": markdown.markdown(body),
                "post_type": "text_only",
                "is_paid": "false",
                "teaser_text": None,
                "thumbnail_position": 0,
                "title": header,
                "post_metadata": {},
                "tags": {
                    "publish": True
                }
            },
            "relationships": {
                "access-rule": {"data": {"type": "access-rule", "id": "18809948"}},
                "user_defined_tags": {"data": []},
                "access_rules": {"data": [{"id": "18809948", "type": "access-rule"}]}
            }
        },
        "included": [{"type": "access-rule", "id": "18809948", "attributes": {}}]
    }
)
_LOGGER.debug(result.content)

post_url = 'https://www.patreon.com/posts/' + post_id

if post_url is not None:
    print('::set-output name=url:: ' + post_url)
else:
    _LOGGER.critical("Got empty post url")
    exit_code = 1

_LOGGER.info("Done")
exit(exit_code)
