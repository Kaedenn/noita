
debug() {
  if [[ -n "$DEBUG" ]]; then
    echo "DEBUG: $@" >&2
  fi
}

repr() {
  declare -p $1 | sed -e 's/^declare \(-[a-z-]\( \)\?\)\?//'
}

decode_rval() {
  case $retval in
    0) printf "\033[1;92mmatched\033[0m";;
    1) printf "\033[1;93mno match\033[0m";;
    2) printf "\033[1;31mregex error\033[0m";;
    *) printf "\033[1;3;91other exit status $retval\033[0m";;
  esac
}

test_match() {
  local quote_pat=0
  local test_str="$1"
  local test_pat="$2"
  if [[ "$1" == "-q" ]]; then
    quote_pat=1
    test_str="$2"
    test_pat="$3"
    printf "matching \`\033[3;92m%q\033[0m\` against \"\033[3;92m%q\033[0m\": " "$test_str" "$test_pat"
  else
    printf "matching \`\033[3;92m%q\033[0m\` against \033[3;92m%q\033[0m: " "$test_str" "$test_pat"
  fi

  local retval=
  if [[ -n "$DEBUG" ]]; then set -x; fi
  if [[ $quote_pat -eq 0 ]]; then
    [[ $test_str =~ $test_pat ]]
  else
    [[ $test_str =~ "$test_pat" ]]
  fi
  retval=$?
  set +x

  echo $(decode_rval $retval)
}

foo() {
  local test_str="$1"
  for pat in "${@:2}"; do
    test_match "$test_str" "$pat"
    test_match -q "$test_str" "$pat"
  done
}

foo $@
