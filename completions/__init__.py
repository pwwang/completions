#!/usr/bin/env python
"""
Generate completions for shells
"""
import re
import sys
import uuid
import warnings
from os import path, sep, rename, makedirs, environ
from simpleconf import Config
from completions.templates import assembleBashWithCommands, assembleBashWithoutCommands, \
	assembleFishWithCommands, assembleFishWithoutCommands, \
	assembleZshWithCommands, assembleZshWithoutCommands


def checkOptname(optname):
	"""Send warning if necessary"""
	if optname.startswith('--') and len(optname) <= 3:
		warnings.warn('Long option %r specified, but the name has length < 2' % optname)
	if optname.startswith('-') and not optname.startswith('--') and len(optname) > 2:
		warnings.warn('Short option %r specified, but the name has length > 1' % optname)

def log(msg, *args):
	"""simple log on the screen"""
	sys.stderr.write('- %s\n' % (msg % args))

class CompletionsLoadError(Exception):
	"""Raises while failed to load completions from configuration file"""

class Command:
	"""A command"""
	def __init__(self, name, desc, options = None):
		self.name = name
		self.desc = desc
		self.options = options or {}

	def addOption(self, opt, desc):
		"""
		Add option to a command
		"""
		if isinstance(opt, list):
			for option in opt:
				self.options[option] = desc
		else:
			self.options[opt] = desc

class Completions(Command):
	"""Completions class"""
	def __init__(self, name = None, desc = None, options = None, inherit = True, fullpath = None):
		super(Completions, self).__init__(name, desc, options)
		self.name     = name or sys.argv[0]
		self.desc     = desc or ''
		self.inherit  = True
		self.commands = {}
		self.inherit  = inherit
		self.uid      = None
		self.fullpath = fullpath and path.realpath(fullpath)

		if sep in self.name:
			self.fullpath = self.fullpath or path.realpath(self.name)
			self.name = path.basename(self.name)

	@property
	def availname(self):
		"""Make an available for function name"""
		return re.sub(r'[^\w_]+', '_', path.basename(self.name))

	def addCommand(self, name, desc, options = None):
		"""Add a command to the completions"""
		self.commands[name] = Command(name, desc, options)

	def command(self, name):
		"""Get the command object by given name"""
		return self.commands[name]

	def _automateFish(self, source):
		compfile = path.expanduser('~/.config/fish/completions/%s.fish' % self.name)
		backfile = compfile + '.completions.bak'
		if path.isfile(compfile):
			log('Completion file exists: %r', compfile)
			log('Back it up to: %r', backfile)
			rename(compfile, backfile)
		log('Writing completion code to: %r', compfile)
		with open(compfile, 'w') as fcomp:
			fcomp.write(source)
		log('Done, you may need to restart your shell in order for the changes to take effect.')

	def _automateBash(self, source):
		compfile = path.expanduser('~/.bash_completion.d/%s.bash-completion' % self.name)
		compdir  = path.dirname(compfile)
		backfile = compfile + '.completions.bak'
		if not path.isdir(compdir):
			log('User completion directory does not exist.')
			log('Try to create it: %s' % compdir)
			makedirs(compdir)
		entryfile = path.expanduser('~/.bashrc')
		entrybak  = entryfile + '.completions.bak'
		with open(entryfile, 'r') as fentry:
			entry = fentry.read()
		# detect if we've already add entry point
		entry_point = '\n' + \
					  '### Start adding entry point by completions, do NOT modify ###\n' + \
					  'for bcfile in %s/*.bash-completion; do\n' % compdir + \
					  '	[ -f "$bcfile" ] && . $bcfile\n' + \
					  'done\n' + \
					  '### End adding entry point by completions ###\n'

		if entry_point not in entry:
			log('Backup entry point file: %s' % entryfile)
			log('To: %s' % entrybak)
			with open(entryfile, 'a+') as fentry, open(entrybak, 'w') as fbak:
				fbak.write(fentry.read())
				log('Add entry point')
				fentry.write(entry_point)

		if path.isfile(compfile):
			log('Completion file exists: %r', compfile)
			log('Back it up to: %r', backfile)
			rename(compfile, backfile)
		log('Writing completion code to: %r', compfile)
		with open(compfile, 'w') as fcomp:
			fcomp.write(source)
		log('Done, you may need to restart your shell in order for the changes to take effect.')


	def _automateZsh(self, source):
		compfile = path.expanduser('~/.zsh-completions/_%s' % self.name)
		compdir  = path.dirname(compfile)
		backfile = path.expanduser('~/.zsh-completions/.%s.completions.bak' % self.name)
		if not path.isdir(compdir):
			log('User completion directory does not exist.')
			log('Try to create it: %s' % compdir)
			makedirs(compdir, mode = 0o755)
		entryfile = path.expanduser('~/.zshrc')
		entrybak  = entryfile + '.completions.bak'
		with open(entryfile, 'r') as fentry:
			entry = fentry.read()
		# detect if we've already add entry point

		if 'compinit' in entry:
			entry_point = '\n' + \
				'### Start adding entry point by completions, do NOT modify ###\n' + \
				'fpath+=%s\n' % compdir + \
				'### End adding entry point by completions ###\n'
		else:
			log('compinstall not found in %s' % entryfile)
			log('Add it (to disable: add `#cominit`).')
			entry_point = '\n' + \
				'### Start adding entry point by completions ###\n' + \
				'zstyle :compinstall filename %r\n' % entryfile + \
				'autoload -Uz compinit\n' + \
				'fpath+=%s\n' % compdir + \
				'# blow may take some time to start, you may want to comment it out\n' + \
				'# and set up the compinit by yourself.\n' + \
				'rm -f ~/.zcompdump; compinit -C\n' + \
				'### End adding entry point by completions ###\n'

		if '# Start adding entry point by completions' not in entry:
			log('Backup entry point file: %s' % entryfile)
			log('To: %s' % entrybak)
			with open(entryfile, 'r') as fentry, open(entrybak, 'w') as fbak:
				entrysrc = fentry.read()
				fbak.write(entrysrc)
			log('Add entry point')

			compinit_index = None
			entrylines = entrysrc.splitlines()
			for i, line in enumerate(reversed(entrylines)):
				if 'cominit' in line and not line.startswith('#'):
					compinit_index = i
					break
			if compinit_index is None:
				entrysrc += entry_point
			else:
				entrylines.insert(compinit_index, entry_point)
				entrysrc = '\n'.join(entrylines)
			with open(entryfile, 'w') as fentry:
				fentry.write(entrysrc)

		if path.isfile(compfile):
			log('Completion file exists: %r', compfile)
			log('Back it up to: %r', backfile)
			rename(compfile, backfile)
		log('Writing completion code to: %r', compfile)
		with open(compfile, 'w') as fcomp:
			fcomp.write(source)
		log('Done, you may need to restart your shell in order for the changes to take effect.')

	def _generateBash(self):
		if self.commands:
			return assembleBashWithCommands(self.name,
				'_%s_%s_complete' % (self.availname, self.uid),
				self.options, self.commands, self.fullpath)
		return assembleBashWithoutCommands(self.name,
			'_%s_%s_complete' % (self.availname, self.uid),
			self.options, self.fullpath)

	def _generateFish(self):
		if self.commands:
			return assembleFishWithCommands(self.name,
				'_%s_%s_complete' % (self.availname, self.uid),
				self.options, self.commands, self.fullpath)
		return assembleFishWithoutCommands(self.name,
			'_%s_%s_complete' % (self.availname, self.uid),
			self.options, self.fullpath)

	def _generateZsh(self):
		if self.commands:
			return assembleZshWithCommands(self.name,
				'_%s_%s_complete' % (self.availname, self.uid),
				self.options, self.commands, self.fullpath)
		return assembleZshWithoutCommands(self.name,
			'_%s_%s_complete' % (self.availname, self.uid),
			self.options, self.fullpath)

	def _inherit(self):
		if not self.inherit:
			return
		for _, command in self.commands.items():
			command.options.update(self.options)

	def generate(self, shell, auto = False):
		"""Generate the completion code"""
		self.uid = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.name)).split('-')[-1]
		if shell == 'auto':
			shell = re.sub(r'[^\w].*', '', path.basename(environ['SHELL']))
			return self.generate(shell, auto)
		self._inherit()
		if shell == 'fish':
			source = self._generateFish()
			if not auto:
				return source
			self._automateFish(source)
		elif shell == 'bash':
			source = self._generateBash()
			if not auto:
				return source
			self._automateBash(source)
		elif shell == 'zsh':
			source = self._generateZsh()
			if not auto:
				return source
			self._automateZsh(source)
		else:
			raise ValueError('Currently only bash, fish and zsh supported.')

	def load(self, dict_var):
		"""Load commands and options from a dict"""
		# integrity check
		if 'program' not in dict_var:
			raise CompletionsLoadError("No 'program' key found.")

		program = dict_var['program']
		if 'name' not in program:
			raise CompletionsLoadError("A program name should be given by 'program.name'")
		self.name = program['name']
		self.desc = program['desc']
		if sep in self.name:
			self.fullpath = path.realpath(self.name)
			self.name = path.basename(self.name)

		for key, val in program.get('options', {}).items():
			self.addOption(key, val)

		self.inherit = dict_var.get('inherit', True)
		commands = dict_var.get('commands', '')
		for key, val in commands.items():
			if not isinstance(val, dict):
				val = {'desc': val}
			options = val.get('options', {})
			self.addCommand(
				name    = key,
				desc    = val.get('desc') or '',
				options = options
			)

	def loadFile(self, compfile):
		"""Load commands and options from a configuration file"""
		config = Config(with_profile = False)
		config._load(compfile)
		self.load(config)

def main():
	"""Entry point of the script"""
	from pyparam import commands
	commands._desc = 'Shell completions for your program made easy.'
	commands._.shell          = 'auto'
	commands._.shell.desc     = [
		'The shell, one of bash, fish, zsh and auto.',
		'Shell will be detected from `os.environ["SHELL"]` if auto.',
	]
	commands._.auto           = False
	commands._.auto.desc      = [
		'Automatically write completions to destination file.',
		'Bash: `~/bash_completion.d/<name>.bash-completion`',
		'  Also try to source it in ~/.bash_completion',
		'Fish: `~/.config/fish/completions/<name>.fish`',
		'Zsh:  `~/.zsh-completions/_<name>`',
		'  `fpath+=~/.zsh-completions` is ensured to add before `compinit`'
	]
	commands._.a                  = commands._.auto
	commands._.s                  = commands._.shell
	commands.self                 = 'Generate completions for myself.'
	commands.self._hbald          = False
	commands.generate             = 'Generate completions from configuration files'
	commands.generate.config.desc = [ # pylint: disable=no-member
		'The configuration file. Scheme should be aligned following schema:',
		'```yaml',
		'program:',
		'    name: completions',
		'    desc: Shell completions for your program made easy.',
		'    path: /absolute/path/to/completions',
		'    inherit: true',
		'    options:',
		'        -s: The shell, one of bash, fish, zsh and auto.',
		'        --shell: The shell, one of bash, fish, zsh and auto.',
		'        -a: Automatically write completions to destination file.',
		'        --auto: Automatically write completions to destination file.',
		'commands:',
		'    self: Generate completions for myself.',
		'    generate:',
		'        desc: Generate completions from configuration files.',
		'        options:',
		'            -c: The configuration file to load.',
		'            --config: The configuration file to load.',
		'```',
		'Configuration file that is supported by `python-simpleconf` is supported.'
	]
	commands.generate.config.required = True       # pylint: disable=no-member
	commands.generate.c = commands.generate.config # pylint: disable=no-member
	command, options, goptions = commands._parse()

	auto = goptions['auto']
	if command == 'self':
		source = commands._complete(goptions['shell'], auto = auto)
		if not auto:
			print(source)
	else:
		completions = Completions()
		completions.loadFile(options['config'])
		source = completions.generate(goptions['shell'], auto = auto)
		if not auto:
			print(source)

if __name__ == '__main__':
	main()
