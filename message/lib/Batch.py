'''
由于restful对于批量不是很友好，故参考https://www.npmjs.com/package/restful-api

POST /api/resource/batch/
    Body: {
                "method": "create",
                "data": [ { "name": "Mr.Bean" }, { "name": "Chaplin" }, { "name": "Jim Carrey" } ]
            }

POST /api/resource/batch/
    Body: {
                "method": "read",
                "data": [1, 2, 3]
            }

POST /api/resource/batch/
    Body: {
                "method": "update",
                "data": { "1": { "name": "Mr.Bean" }, "2": { "name": "Chaplin" } }
            }

POST /api/resource/batch/
    Body: {
                "method": "delete",
                "data": [1, 2, 3]
            }
'''

from rest_framework import viewsets
from rest_framework.response import Response

from message.lib import Cipher

base62_cipher = Cipher.Base62Cipher()


class BatchGenericViewSet(viewsets.GenericViewSet):
    batch_method_names = ('create', 'read', 'update', 'delete')

    def batch_method_not_allowed(self, request, *args, **kwargs):
        method = request.batch_method
        raise exceptions.MethodNotAllowed(
            method, detail=f'Batch Method {method.upper()} not allowed.')

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # 将batch_method从请求体中提取出来，方便后面使用
        batch_method = request.data.get('method', None)
        if batch_method is not None:
            request.batch_method = batch_method.lower()
        else:
            request.batch_method = None
        return request

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers
        try:
            self.initial(request, *args, **kwargs)
            # 首先识别batch_method并进行分发
            if request.batch_method in self.batch_method_names:
                method_name = 'batch_' + request.batch_method.lower()
                handler = getattr(self, method_name,
                                  self.batch_method_not_allowed)
            elif request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request, response, *args, **kwargs)
        return self.response


class BatchMixin:

    def batch_create(self, request, *args, **kwargs):
        data = request.data.get('data', None)
        if not isinstance(data, list):
            raise exceptions.ValidationError({'data': 'Data must be a list.'})
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def batch_read(self, request, *args, **kwargs):
        data = request.data.get('data', None)
        # id= int(id) if str.isdigit(id) else base62_cipher.str62_to_int(id)
        # ids = [int(id) for id in data]
        ids = [int(id) if str.isdigit(
            id) else base62_cipher.str62_to_int(id) for id in data]
        if not isinstance(data, list):
            raise exceptions.ValidationError({'data': 'Data must be a list.'})
        queryset = self.get_queryset().filter(uid__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def batch_update(self, request, *args, **kwargs):
        data = request.data.get('data', None)
        if not isinstance(data, dict):
            raise exceptions.ValidationError(
                {'data': 'Data must be a object.'})
        # ids = [int(id) for id in data]
        ids = [int(id) if str.isdigit(
            id) else base62_cipher.str62_to_int(id) for id in data]
        queryset = self.get_queryset().filter(id__in=ids)
        results = []
        for obj in queryset:
            serializer = self.get_serializer(
                obj, data=data[str(obj.id)], partial=True)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                self.perform_update(serializer)
            results.append(serializer.data)
        return Response(results)

    def batch_delete(self, request, *args, **kwargs):
        data = request.data.get('data', None)
        ids = [int(id) if str.isdigit(
            id) else base62_cipher.str62_to_int(id) for id in data]
        if not isinstance(data, list):
            raise exceptions.ValidationError({'data': 'Data must be a list.'})
        queryset = self.get_queryset().filter(id__in=ids)
        with transaction.atomic():
            self.perform_destroy(queryset)
        return Response(status=status.HTTP_204_NO_CONTENT)
