"""Policy regressions shared by static checks and the actual Wazuh runner."""

def regression_cases():
    def event(action, **fields):
        return dict(integration='mcp_lab', mcp_action=action, **fields)

    cases = [
        ('unrelated source', dict(integration='other', mcp_action='file_read', path='/home/lab/.ssh/id_ed25519'), None),
        ('ordinary process', event('process_start', executable='/usr/bin/python3'), None),
        ('ordinary send', event('network_send', source_path='/tmp/public.txt', sensitive='yes'), None),
        ('missing path', event('file_read', sensitive='yes'), None),
        ('sensitive label cannot promote public path', event('file_read', path='/tmp/public.txt', sensitive='yes'), None),
        ('missing transfer source', event('network_send', sensitive='yes'), None),
    ]
    for path in ['/home/lab/.ssh/id_ed25519', '~/.ssh/config', '/srv/app/.env', '/srv/app/.env.production', '/home/lab/.aws/credentials', '/home/lab/.kube/config']:
        cases.append(('read '+path, event('file_read', path=path), '110501'))
        cases.append(('read label no '+path, event('file_read', path=path, sensitive='no'), '110501'))
        cases.append(('send '+path, event('network_send', source_path=path, sensitive='no'), '110503'))
    for path in ['/tmp/not.env', '/tmp/.envdir/file', '/tmp/.ssh-backup/key', '/home/lab/.aws/credentials.bak', '/home/lab/.kube/configuration']:
        cases.append(('public '+path, event('file_read', path=path, sensitive='yes'), None))
    for prefix in ['/bin/', '/usr/bin/', '/usr/local/bin/']:
        for shell in ['sh', 'bash', 'dash', 'zsh', 'ksh', 'ash']:
            cases.append(('shell '+prefix+shell, event('process_start', executable=prefix+shell), '110502'))
    for exe in ['/usr/bin/bashful', '/tmp/bash', '/usr/bin/env']:
        cases.append(('other executable '+exe, event('process_start', executable=exe), None))
    for exe in ['/usr/bin/python3', '/bin/python', '/usr/local/bin/python3.12']:
        cases.append(('inline '+exe, event('process_start', executable=exe, argument1='-c'), '110504'))
        cases.append(('script '+exe, event('process_start', executable=exe, argument1='app.py'), None))
    for exe in ['/usr/bin/node', '/usr/local/bin/node', '/bin/nodejs']:
        for flag in ['-e', '--eval']:
            cases.append(('inline '+exe+' '+flag, event('process_start', executable=exe, argument1=flag), '110505'))
        cases.append(('script '+exe, event('process_start', executable=exe, argument1='app.js'), None))
    cases.append(('wrong action', event('file_read', executable='/bin/bash'), None))
    return cases
