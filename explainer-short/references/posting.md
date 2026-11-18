# Posting as an Instagram trial reel (the setup the format won with)

Only when the user asks. Confirm the account first. The steps below use Blotato (if connected: `blotato_list_accounts`, then pick the user's Instagram account with them). Without a scheduler, give the user the video, cover.jpg, caption and first comment, and the settings to choose in the Instagram app: trial reel, not shared to feed.

## Per video

1. `blotato_create_presigned_upload_url` for the .mp4 (use the full-quality render, not the share copy), then upload it:
   `curl -s -o /dev/null -w "%{http_code}" -X PUT "<presignedUrl>" -H "Content-Type: video/mp4" --data-binary "@<file>"` (expect 200).
   Confirm the size: `curl -sI <publicUrl>` Content-Length must equal the local file size.
2. Cover: `ffmpeg -v error -y -ss 1.5 -i <file> -frames:v 1 -q:v 2 -update 1 cover.jpg`. Look at it, then upload it the same way with `image/jpeg`.
3. `blotato_create_post`:
   - `accountId` = the user's Instagram account id, `platform` "instagram", `mediaType` "reel"
   - `mediaUrls` [video publicUrl], `coverImageUrl` cover publicUrl
   - `shareToFeed` false, `trial` {"graduationStrategy": "MANUAL"}
   - `text`: the caption (template below), **at most 5 hashtags**
   - `firstComment`: the link line
   - `scheduledTime` (ISO 8601 UTC) for later posts. **Never `scheduledAt`, never `useNextFreeSlot`.** Call `blotato_list_schedules` first and avoid the account's other posts.
4. Post the first one immediately as a canary. Poll `blotato_get_post_status` (at least 10 s apart) until it is `published`. Then schedule the rest. Ask the user to check in the app that the reel is **not** on the profile grid (that shows the trial flag took) and that the first comment posted.
5. Show times in the user's own time zone, never raw UTC.

## Caption that ran with the winner

```
<One line: what the viewer can now do>. 5 steps:

1. <step 1>
2. <step 2>
3. <step 3>
4. <step 4>
5. <step 5>

Link in the first comment. Save this for later.

#<tag> #<tag> #<tag> #<tag> #<tag>
```

First comment: the link the end card points to (or the user's CTA).

## After posting

- Pull metrics 48 h later (with Blotato: `blotato_list_posts`, platform instagram, status published) and tell the user how it did.
