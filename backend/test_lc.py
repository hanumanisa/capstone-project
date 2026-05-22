from api.models import User
from api.ai_agent import current_user_id_var, execute_ai_query
from api.ai_tools import get_tna_status

u = User.objects.get(username='andi.kusuma319@ptsmi.co.id')
print("Direct Tool Call:", get_tna_status.invoke({'user_id': u.id}))

tok = current_user_id_var.set(u.id)
res = execute_ai_query(u, 'halo?')
print("AGENT_OUTPUT:", res)
current_user_id_var.reset(tok)
