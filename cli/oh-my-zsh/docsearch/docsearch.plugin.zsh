# Docsearch basic command completion
_docsearch_get_command_list () {
	./docsearch --no-ansi | sed "1,/Available commands/d" | awk '/^  [a-z]+/ { print $1 }'
}

_docsearch () {
  if [ -f docsearch ]; then
  	if [ $words[1] = './docsearch' ]; then
  		if (( CURRENT == 2 )); then
			compadd `_docsearch_get_command_list`
		else
			_files && ret=0
		fi
    fi
  fi
}

compdef _docsearch docsearch

#Alias
alias docsearch='./docsearch'