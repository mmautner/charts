#!/bin/sh
# Download the primary documents into raw/. Run from the post folder: sh inputs/fetch.sh
# raw/ is not committed. The charts read only data/, which is hand-transcribed from these files
# (each row cites its URL and table or page).
set -u
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
mkdir -p raw/chicago raw/iihs raw/fhwa
get() { curl -sfL -A "$UA" -o "$1" "$2" || echo "missing: $1 ($2)"; }

# Sutton & Tilahun (UIC), report to the City of Chicago, Jan. 30, 2022. chicago.gov blocks scripted
# downloads (403), so this pulls the Wayback Machine's copy of the same URL. Table 1 (PDF page 36,
# printed page 33) is an image in the PDF.
CHI='www.chicago.gov/content/dam/city/depts/cdot/Red%20Light%20Cameras/2022/Sutton+Tilahun_CDOT-Cameras-FinalReport.pdf'
get raw/chicago/sutton_tilahun_2022.pdf "https://web.archive.org/web/2023id_/https://$CHI"

# Hu & Cicchino (2017), Journal of Safety Research 61:141-148, doi:10.1016/j.jsr.2017.02.019. The full text
# is paywalled at ScienceDirect; IIHS's bibliography page carries the abstract and its news release the
# same four headline figures.
get raw/iihs/hu_cicchino_2017_bibliography.html https://www.iihs.org/research-areas/bibliography/ref/2121
get raw/iihs/news_turning_off_red_light_cameras.html \
    https://www.iihs.org/news/detail/turning-off-red-light-cameras-costs-lives-new-research-shows

# FHWA CMF Clearinghouse entries for both studies (secondary: unrounded values and standard errors)
get raw/fhwa/study_518_hu_cicchino.html "https://cmfclearinghouse.fhwa.dot.gov/study_detail.php?stid=518"
get raw/fhwa/study_682_tilahun.html "https://cmfclearinghouse.fhwa.dot.gov/study_detail.php?stid=682"
for f in 9264 9265 9266 9267 9268 9269 11485 11486 11487 11488; do
  get raw/fhwa/cmf_$f.html "https://cmfclearinghouse.fhwa.dot.gov/detail.php?facid=$f"
done

# IIHS topic pages (updated July 2026). The yearly community counts are the Highcharts series embedded in the
# page source ("Trends in the number of U.S. communities with ... programs"); transcribed to
# data/camera_communities.csv.
get raw/iihs/red_light_running_topic.html https://www.iihs.org/research-areas/red-light-running
get raw/iihs/speed_topic.html https://www.iihs.org/research-areas/speed
