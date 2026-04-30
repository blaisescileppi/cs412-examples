def user_profiles(request):
    """Safely inject doctor_profile and patient_profile into every template."""
    ctx = {'doctor_profile': None, 'patient_profile': None}
    if request.user.is_authenticated:
        try:
            ctx['doctor_profile'] = request.user.doctor_profile
        except Exception:
            pass
        try:
            ctx['patient_profile'] = request.user.patient_profile
        except Exception:
            pass
    return ctx
