import pytermor as pt

s = """:[fg=red]nested for:[bold]mat:[bg=blue]ting a:[fg=yellow]nd :[-]over:[-]laps"""
pt.echo(pt.TemplateEngine().substitute(s))
