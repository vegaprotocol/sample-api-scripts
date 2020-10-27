#!/usr/bin/env bash

check_var() {
	var_name="$1"
	var_value="${!var_name}"
	if [[ -z "$var_value" ]] ; then
		echo "Invalid $var_name - empty"
		return 1
	fi
	if echo "$var_value" | grep -q example ; then
		echo "Invalid $var_name - contains \"example\""
		return 1
	fi
}

check_url() {
	var_name="$1"
	check_var "$var_name" || return 1
	var_value="${!var_name}"
	if ! echo "$var_value" | grep -qE '^http[s]?://' ; then
		echo "Invalid $var_name - does not start with \"http://\" or \"https://\""
		return 1
	fi
}
