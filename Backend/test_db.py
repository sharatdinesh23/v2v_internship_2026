from database import supabase
try:
    profiles = supabase.table('Profiles').select('email, name, Roles(role_name)').execute().data
    print('ALL PROFILES:')
    for p in profiles:
        role_name = p['Roles']['role_name'] if p.get('Roles') else 'None'
        if isinstance(p.get('Roles'), list):
            role_name = p['Roles'][0]['role_name'] if p['Roles'] else 'None'
        print(f" - {p['email']}: {p['name']} ({role_name})")
except Exception as e:
    import traceback
    traceback.print_exc()
