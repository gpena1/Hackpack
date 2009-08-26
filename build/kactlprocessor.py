#!/usr/bin/env python
# encoding: utf-8

# Source code preprocessor for KACTL building process.
# Written by Håkan Terelius, 2008-11-24

import sys
import getopt


def escape(input):
	input = input.replace('<','\\ensuremath{<}')
	input = input.replace('>','\\ensuremath{>}')
	return input

def pathescape(input):
	input = input.replace('\\','\\\\')
	input = input.replace('_','\_')
	input = escape(input)
	return input

def codeescape(input):
	input = input.replace('_','\\_')
	input = input.replace('\n','\\\\\n')
	input = input.replace('{','\\{')
	input = input.replace('}','\\}')
	input = input.replace('^','\\ensuremath{\\hat{\\;}}')
	input = escape(input)
	return input

def ordoescape(input):
	input = escape(input)
	start = input.find("O(")
	if start >= 0:
		bracketcount = 1
		end = start+1
		while end+1<len(input) and bracketcount>0:
			end = end + 1
			if input[end] is '(':
				bracketcount = bracketcount + 1
			elif input[end] is ')':
				bracketcount = bracketcount - 1
		if bracketcount == 0:
			return input[:start] + "\\bigo{" + input[start+2:end] + "}" + ordoescape(input[end+1:])
	return input

def processwithcomments(caption, instream, outstream, listingslang = None):
	knowncommands = ['Author', 'Date', 'Description', 'Source', 'Time', 'Memory', 'Status', 'Usage', 'Changes']
	requiredcommands = ['Author', 'Date', 'Source', 'Description']
	includelist = ""
	error = ""
	warning = ""
	# Read lines from source file
	try:
		lines = instream.readlines()
	except:
		error = "Could not read source."
	nlines = list()
	for line in lines:
		# Remove /// comments
		line = line.split("///")[0].rstrip()
		# Remove '#pragma once' and 'using namespace std;' lines
		if line == "#pragma once" or line == "using namespace std;":
			continue
		# Check includes
		include = isdefaultinclude(line)
		if include is None:
			nlines.append(line)
		elif len(include)>0:
			if len(includelist)>0:
				includelist = includelist + ", " + include
			else:
				includelist = include
	# Remove and process /** */ comments
	source = '\n'.join(nlines)
	nsource = ''
	start = source.find("/**")
	end = 0
	commands = dict()
	while start >= 0 and not error:
		nsource = nsource.rstrip() + source[end:start]
		end = source.find("*/", start)
		if end<start:
			error = "Invalid /** */ comments."
			break
		comment = source[start+3:end].strip()
		end = end + 2
		start = source.find("/**",end)

		commentlines = comment.split('\n')
		command = None
		value = ""
		for cline in commentlines:
			cline = cline.strip()
			if cline.startswith('*'):
				cline = cline[1:].strip()
			ind = cline.find(':')
			if ind>-1 and cline[:ind].find(' ')==-1:
				if command:
					if command not in knowncommands:
						warning = warning + "Unknown command: " + command + ". "
					commands[command]=value.lstrip()
				command = cline[:ind]
				value = cline[ind+1:].strip()
			else:
				value = value + '\n' + cline
		if command:
			if command not in knowncommands:
				warning = warning + "Unknown command: " + command + ". "
			commands[command]=value.lstrip()
	for rcommand in requiredcommands:
		if not rcommand in commands:
			error = error + "Missing command: " + rcommand + ". "
	if end>=0:
		nsource = nsource.rstrip() + source[end:]
	nsource = nsource.strip()

	# Produce output
	if warning:
		print >> outstream, "\kactlwarning{",caption,":",warning,"}"
	if error:
		print >> outstream, "\kactlerror{",caption,":",error,"}"
	else:
		print >> outstream, "\\kactlref{",pathescape(caption),"}"
		if "Description" in commands and len(commands["Description"])>0:
			print >> outstream, "\\defdescription{",escape(commands["Description"]),"}"
		if "Usage" in commands and len(commands["Usage"])>0:
			print >> outstream, "\\defusage{",codeescape(commands["Usage"]),"}"
		if "Time" in commands and len(commands["Time"])>0:
			print >> outstream, "\\deftime{",ordoescape(commands["Time"]),"}"
		if "Memory" in commands and len(commands["Memory"])>0:
			print >> outstream, "\\defmemory{",ordoescape(commands["Memory"]),"}"
		if len(includelist)>0:
			print >> outstream, "\\leftcaption{",pathescape(includelist),"}"
		print >> outstream, "\\rightcaption{",str(linecount(nsource))," lines}"
		print >> outstream, "\\begin{lstlisting}[caption={",pathescape(caption),"}",
		if listingslang is not None:
			print >> outstream, ", language="+listingslang,
		print >> outstream, "]"
		print >> outstream, nsource
		print >> outstream, "\\end{lstlisting}"

def processraw(caption, instream, outstream, listingslang = 'raw'):
	try:
		source = instream.read().strip()
		print >> outstream, "\\kactlref{",pathescape(caption),"}"
		print >> outstream, "\\rightcaption{",str(linecount(source))," lines}"
		print >> outstream, "\\begin{lstlisting}[language="+listingslang+",caption={",pathescape(caption),"}]"
		print >> outstream, source
		print >> outstream, "\\end{lstlisting}"
	except:
		print >> outstream, "\kactlerror{Could not read source.}"

def linecount(source):
	return source.count("\n")+1

def isdefaultinclude(line):
	defaultinclude = ['<iostream>', '<algorithm>', '<string>', '<vector>', '<cmath>', '<queue>', '<map>', '<set>']
	line = line.strip()
	if line.startswith("#include"):
		line = line[8:].strip()
		if line in defaultinclude:
			return ""
		else:
			return line
	return None
	
def getlang(input):
	return input.rsplit('.',1)[-1]

def getfilename(input):
	return input.rsplit('/',1)[-1]

def main(argv=None):
	language = None
	caption = None
	instream = sys.stdin
	outstream = sys.stdout
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(argv[1:], "ho:i:l:c:", ["help", "output=", "input=", "language=", "caption="])	
		for option, value in opts:
			if option in ("-h", "--help"):
				print "This is the help section for this program"
				print
				print "Available commands are:"
				print "\t -o --output"
				print "\t -h --help"
				print "\t -i --input"
				print "\t -l --language"
				return
			if option in ("-o", "--output"):
				outstream = open(value, "w")
			if option in ("-i", "--input"):
				instream = open(value)
				if language == None:
					language = getlang(value)
				if caption == None:
					caption = getfilename(value)
			if option in ("-l", "--language"):
				language = value
			if option in ("-c", "--caption"):
				caption = value
		print "Processing", caption	
		if language == "cpp" or language == "cc" or language == "c" or language == "h" or language == "hpp":
			processwithcomments(caption, instream, outstream)
		elif language == "java":
			processwithcomments(caption, instream, outstream, 'Java')
		elif language == "ps":
			processraw(caption, instream, outstream) # PostScript was added in listings v1.4
		elif language == "raw":
			processraw(caption, instream, outstream)
		elif language == "sh":
			processraw(caption, instream, outstream, 'bash')
		else:
			raise ValueError("Unkown language: " + str(language))
	except (ValueError, getopt.GetoptError, IOError), err:
		print >> sys.stderr, str(err)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
