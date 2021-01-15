'''
自定义返回处理
'''

# 导入控制返回的JSON格式的类
from rest_framework.renderers import JSONRenderer


class customrenderer(JSONRenderer):
    # 重构render方法
    def render(self, data, accepted_media_type=None, renderer_context=None):

        status_code = renderer_context['response'].status_code
        print('重构render方法', status_code)
        if renderer_context:
            msg = ''
            status = status_code
            if data:
                if isinstance(data, dict):
                    msg = data.pop('msg', 'success')
                    status = data.pop('status', status_code)
                elif isinstance(data, list):
                    # 需返回count字段来统计数组大小
                    msg = 'success'
                    result = {
                        'count': len(data),
                        'results': data
                    }
                    data = result
                else:
                    msg = 'fail'
                    status = status_code
                # 重新构建返回的JSON字典
                for key in data:
                    # 判断是否有自定义的异常的字段
                    if key == 'exception_message':
                        msg = data[key]
                        status = -1
                        data = ''
            # 落在200-300范围内都是成功的，返回data
            if status_code < 200 or status_code > 300:
                msg = 'fail'
            ret = {
                'message': msg,
                'status': status,
                'data': data,
            }

            # 返回JSON数据
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)
