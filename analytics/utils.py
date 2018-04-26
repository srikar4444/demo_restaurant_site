
# in order for this code to make sense search how ip_address is tracked in django
# this is for taking in ip_address of user
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(",") [0]
    else :
        ip = request.META.get("REMOTE_ADDR", None)

    return ip