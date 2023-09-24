import pytermor as pt

s = """@st:[fg=yellow bold] @cmd:[fg=green]
:[st]grow, mark and tweak your common history:[-]
   :[cmd]branch:[-]            List, create, or delete branches
   :[cmd]commit:[-]            Record changes to the repository
   :[cmd]merge:[-]             Join two or more development histories together
"""
pt.echo(pt.TemplateEngine().substitute(s))
