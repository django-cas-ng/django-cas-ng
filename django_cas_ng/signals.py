from django import dispatch

cas_user_authenticated = dispatch.Signal(
    providing_args=['user', 'created', 'attributes', 'ticket', 'service'],
)
