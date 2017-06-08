#! /bin/bash

prefix="TILE_"

x=1
y=1
dims=""


# ====================================
# Check for ImageMagick
# ====================================
if ! hash convert 2>/dev/null; then
	printf "You must have ImageMagick installed to use ${0}"
	exit 1
fi


# ==================
# Vars
# ==================
# Read files from command line args
files=()

# Color codes
esc="\033"
red="${esc}[0;31m"
green="${esc}[0;32m"
yellow="${esc}[0;33m"
blue="${esc}[0;34m"
cyan="${esc}[0;36m"
reset="${esc}[0;m"


# ==================
# Functions
# ==================
function getcols() {
	tput cols
}

index=1
total=0
function progressbar() {
	cols=$(getcols)
	bar="\r"
	left="$1"
	right="${index}/${total} "
	skip="$2"

	(( barload = cols - ${#right} ))
	if [ "$skip" = true ]; then
		(( div = total / barload ))
		(( div = div > 0 ? div : 1 ))
		if (( index > 1 && index % div != 0 )); then
			return # Only print if progress bar advances
		fi
		left="(Skipping) ${left}"
	fi

	# Progress section
	spaced=false # Put spaces in between progress bar characters
	begin=""     # For color: e.g., begin="$red"
	end=""       #                  end="$reset"
	advance="▮█▰⣿◼.⬜"
	remain="▯░▱⣀▭ ⣿"
	charset=3 # Pick a charset for the progress bar (0 to 6)

	advance="${advance:$charset:1}"
	remain="${remain:$charset:1}"

	(( load = cols - ${#right} - ${#left} ))
	(( mod = load % 2 == 0 ? 1 : 0 ))
	(( progress = index * barload / total ))
	(( progress = progress - ${#left} ))
	(( progress = progress < 0 ? 0 : progress ))

	# Left
	bar="${bar}${yellow}${left}${reset}"
	# Middle
	bar="${bar}${begin}"
	for (( i = 0; i < load; i++ )); do
		if (( i == progress )); then
			bar="${bar}${end}"
		fi

		if (( i < progress )); then
			if [ "$spaced" = true ] && (( i % 2 == mod )); then
				bar="${bar} "
			else
				bar="${bar}${advance}"
			fi
		else
			if [ "$spaced" = true ] && (( i % 2 == mod )); then
				bar="${bar} "
			else
				bar="${bar}${remain}"
			fi
		fi
	done
	# Right
	bar="${bar}${cyan}${right}${reset}"

	printf "$bar"
}

function split() {
	printf "Splitting images into ${x}x${y} tiles:\n"
	SECONDS=0
	converted=0

	for fname in "${files[@]}"; do
		base=${fname##*/} # Basename
		ext=${base##*.}   # Extension only
		noext=${base%.*}  # Remove extension

		skip=false
		for some_file in "${prefix}${noext}"*; do
			# Check if the glob gets expanded to existing files.
			# If not, some_file here will be exactly the pattern
			# above and the exists test will evaluate to false.
			if ! [ -e "$some_file" ]; then
				convert "${fname}" +gravity -crop ${dims} "${prefix}${noext}_%d.${ext}"
				# If there are too many files after converting, delete them
				# (1 or 2 pixels wide leftover from float inaccuracy)
				(( over = x * y))
				fover="${prefix}${noext}_${over}.${ext}"
				if [ -f "$fover" ]; then
					for (( i = x; i <= (x + 1) * y - 1; i += x + 1 )); do
						rm "${prefix}${noext}_${i}.${ext}"
					done
				fi
				(( converted++ ))
			else
				skip=true
			fi

			# This is all we needed to know, so we can break after
			# the first iteration
			break
		done

		progressbar "'${fname}'" "$skip"
		(( index++ ))
	done


	# ==================
	# Output
	# ==================
	clr="\r"
	cols=$(getcols)
	for (( i=0; i<cols; i++ )); do
		clr="${clr} "
	done
	printf "$clr"
	printf "\r${green}Complete!${reset}\n"

	duration=$SECONDS
	(( mins = $duration / 60 ))
	(( secs = $duration % 60 ))

	if (( duration <= 60 )); then
		printf "Tiled ${cyan}${converted}${reset} files in ${cyan}${secs}s${reset}\n"
	else
		printf "Tiled ${cyan}${converted}${reset} files in ${cyan}${mins}m ${secs}s${reset}\n"
	fi
}


# ==================
# Run
# ==================
usage="\
Welcome to image tile manager.\n\
Use   $ ${0} help                          to display this help\n\
      $ ${0} [X] [Y] [IMAGE(S)]            to split image(s) into X by Y tiles\n\
      $ ${0} [X] [Y] [PREFIX] [IMAGE(S)]   to specify a prefix for the tiles\n\
      $ ${0} clean                         to remove tiles\n\
      $ ${0} clean [PREFIX]                to remove tiles with specific prefix\
"

if [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
	printf "$usage\n"
elif [ "$1" == "clean" ]; then
	# Set prefix to 2nd arg, if it exists
	[ -z "$2" ] || prefix="$2"

	printf "Removing all tiles with prefix '${prefix}' ..."
	rm "${prefix}"* 2>/dev/null

	printf "${green}done!${reset}\n"
elif [ $# -lt 3 ] || [ -f "$1" ] || [ -f "$2" ]; then
	printf "$usage\n"
else
	x="$1"
	y="$2"

	[ -f "$3" ] || prefix="$3" # Set prefix to 3rd arg, if it exists

	xpercent=$(bc <<< "scale=3; 100 / ${x}")
	ypercent=$(bc <<< "scale=3; 100 / ${y}")
	# Dimensions (for ImageMagick)
	dims="${xpercent}%x${ypercent}%"

	list=$(printf "%s\n" "$@" | sed "/^${prefix}/d") # Remove files starting with prefix
	IFS=$'\n' read -d '' -r -a files <<< "$list"

	unset files[0]
	unset files[1]
	[ -f "$3" ] || unset files[2]

	total=${#files[@]}

	# Main program
	split
fi
