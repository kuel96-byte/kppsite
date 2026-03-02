import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Pass, AccessLog
from django.core.paginator import Paginator


def index(request):
    """Главная страница с камерой"""
    return render(request, 'index.html')


@csrf_exempt
def scan_qr(request):
    """Обработка сканированного QR-кода"""
    if request.method == 'POST':
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '')

        # Получаем IP для лога
        ip_address = request.META.get('REMOTE_ADDR', '')

        try:
            # Ищем пропуск в базе
            pass_obj = Pass.objects.get(qr_code_data=qr_data)

            # Проверяем действительность
            if pass_obj.is_valid():
                result = 'granted'
                message = 'Доступ разрешен'
            else:
                result = 'expired'
                message = 'Срок действия истек'

        except Pass.DoesNotExist:
            result = 'denied'
            message = 'Пропуск не найден'
            pass_obj = None

        # Логируем попытку
        AccessLog.objects.create(
            pass_data=pass_obj,
            qr_code_scanned=qr_data,
            access_result=result,
            ip_address=ip_address
        )

        return JsonResponse({
            'result': result,
            'message': message,
            'pass_data': {
                'full_name': pass_obj.full_name if pass_obj else None,
                'pass_type': pass_obj.get_pass_type_display() if pass_obj else None,
                'organization': pass_obj.organization if pass_obj else None,
                'photo': pass_obj.photo.url if pass_obj and pass_obj.photo else None
            } if pass_obj else None
        })

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


def generate_qr(request, pass_id):
    """Генерация QR-кода для пропуска (опционально)"""
    from django.http import HttpResponse
    import qrcode
    from io import BytesIO

    pass_obj = get_object_or_404(Pass, id=pass_id)

    # Создаем QR-код
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(pass_obj.qr_code_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Сохраняем в байтовый поток
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')
