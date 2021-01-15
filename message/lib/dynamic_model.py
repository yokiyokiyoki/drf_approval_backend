# -*- coding: utf-8 -*-
"""动态表格
"""

import logging
from copy import copy
from datetime import datetime, timedelta

from django.db import models
from django.db import router
from django.db import connections
from django.utils import timezone
from django.db.utils import OperationalError

from django.apps import apps

import moment


logger = logging.getLogger(__name__)


class ModelSchemaEditor:
    """根据model查看所属的db，并初始化对应的连接
    """
    @classmethod
    def get_connection_with_model(cls, model):
        """根据model获取DB连接
        """
        db = router.db_for_write(model)
        return connections[db]

    @classmethod
    def get_db_tables(cls, connection):
        """查看当前连接DB的表格
        """
        with connection.cursor() as cursor:
            return [table_info.name for table_info in connection.introspection.get_table_list(cursor)]

    @classmethod
    def check_table_exist(cls, model):
        """判断表格是否存在
        """
        db_table = model._meta.db_table
        curr_conn = cls.get_connection_with_model(model)
        if db_table not in cls.get_db_tables(curr_conn):
            return False
        else:
            return True

    @classmethod
    def create_table(cls, new_model):
        """创建表格
        """
        curr_conn = cls.get_connection_with_model(new_model)
        if not cls.check_table_exist(new_model):
            try:
                with curr_conn.schema_editor() as editor:
                    editor.create_model(new_model)
            except OperationalError as err:
                if err.args[0] == 1050:  # Table already exists
                    logger.warning("<model: %s> table has created" %
                                   new_model.__name__)
                    return
                raise

    @classmethod
    def drop_table(cls, model):
        """删除表格
        """
        curr_conn = cls.get_connection_with_model(model)
        try:
            with curr_conn.schema_editor() as editor:
                editor.delete_model(model)
        except OperationalError as err:
            if err.args[0] == 1051:  # Table not exist
                logger.warning("<model: %s> table has dropped" %
                               model.__name__)
                return
            raise


class BaseShardMixin(object):
    """基础分表
    """

    @classmethod
    def shard(cls, shard_key=None, options=None):
        """分表
        """

    @classmethod
    def create_model(cls, sharding, options=None):
        """动态创建model
        """

        if sharding:
            model_name = cls.__name__ + str(sharding)
            table_name = "%s_%s" % (cls._meta.db_table, str(sharding))
        else:
            model_name = cls.__name__
            table_name = cls._meta.db_table

        class Meta:
            db_table = table_name
            unique_together = cls._meta.unique_together
            index_together = cls._meta.index_together

        if options is not None:
            for key, value in options.iteritems():
                setattr(Meta, key, value)

        attrs = {
            '__module__': cls.__module__,
            'Meta': Meta,
        }

        # 动态添加外键
        remote_fields = []
        for field in cls._meta.fields:
            attrs[field.name] = copy(field)
            # copy foreign key, rename 'related_name'
            if isinstance(field, models.ForeignKey):
                remote_field = copy(field.remote_field)
                if remote_field.related_name != "+":
                    remote_field.related_name = '%s_%s' % (
                        remote_field.related_name, sharding)
                remote_field.field = attrs[field.name]
                attrs[field.name].remote_field = remote_field
                remote_fields.append(remote_field)
        ModelClass = type(model_name, (cls,), attrs)
        for remote_field in remote_fields:
            remote_field.to = ModelClass
        return ModelClass


class DateShardMixin(BaseShardMixin):
    """日期分表
    """

    DATEFORMAT = "%Y%m%d"
    DEFAULT_TABLE = "00000000"

    @classmethod
    def shard(cls, date=None, options=None):
        """分表处理
        """
        if cls._compare_date(date):
            date_str = cls._get_date_str(date)
            _db_table = "%s%s" % (cls._meta.db_table, date_str)  # 分表表名
        else:
            date_str = cls.DEFAULT_TABLE
            _db_table = "%s%s" % (cls._meta.db_table, date_str)
            logger.info(
                "current date is invalid: %s, use default table: %s" % (date, _db_table))

        if sharding:
            model_name = cls.__name__ + str(date)
            table_name = "%s_%s" % (cls._meta.db_table, str(date))
        else:
            model_name = cls.__name__
            table_name = cls._meta.db_table
        try:
            model = apps.get_model(cls._meta.app_label, model_name)
            logging.info('已经创建好数据库')
            return model
        except LookupError:
            model = None

        if modele is None:
            new_model = cls.create_model(date_str)
            ModelSchemaEditor.create_table(new_model)
            return new_model

    @classmethod
    def default_model(cls):
        """默认表格
        """
        default_model = cls.create_model(cls.DEFAULT_TABLE)
        ModelSchemaEditor.create_table(default_model)
        return default_model

    @classmethod
    def get_expired_models(cls, expired_date):
        """获取当前Model过期的表格
        """
        curr_conn = ModelSchemaEditor.get_connection_with_model(cls)
        tables = ModelSchemaEditor.get_db_tables(curr_conn)
        current_model_tables = []
        for table_name in tables:
            if table_name.startswith(cls._meta.db_table):
                current_model_tables.append(table_name)
        expired_models = []
        for table in current_model_tables:
            table_date_str = table.replace(cls._meta.db_table, "").lstrip("_")
            if table_date_str == cls.DEFAULT_TABLE:
                continue
            try:
                table_date = timezone.make_aware(
                    datetime.strptime(table_date_str, cls.DATEFORMAT))
                if table_date < expired_date:
                    model_class = cls.create_model(sharding=table_date_str)
                    expired_models.append(model_class)
            except Exception as err:
                logger.warning("[Model:%s] get expired model failed, err: %s" % (
                    cls._meta.db_table, err))
                continue
        return expired_models

    @classmethod
    def delete_model(cls, model):
        """删除指定Model的表格
        """
        ModelSchemaEditor.drop_table(model)

    @classmethod
    def _get_date_str(cls, date):
        """获取时间字符串
        """
        localdate = timezone.localdate(date)
        logger.info("current local date: %s, date: %s" % (localdate, date))
        return localdate.strftime(cls.DATEFORMAT)

    @classmethod
    def _compare_date(cls, date):
        """判断传入的时间是否跟当前时间间隔7天
        如果间隔7天以上则无效，返回False，间隔7天内则有效，返回True
        """
        localdate = timezone.localdate(date)
        now_date = datetime.now().date()
        if localdate < now_date - timedelta(days=7):
            return False
        else:
            return True


class MonthShardMixin(DateShardMixin):
    """
    按月分表
    """
    DATEFORMAT = "%Y%m"
    DEFAULT_TABLE = "000000"

    @classmethod
    def shard(cls, date=None, options=None):
        """分表处理
        """

        date_str = cls._get_date_str(date)
        _db_table = "%s%s" % (cls._meta.db_table, date_str)  # 分表表名

        new_model = cls.create_model(date_str)
        ModelSchemaEditor.create_table(new_model)
        return new_model

    @classmethod
    def _get_date_str(cls, date):
        """获取时间字符串
        """

        if isinstance(date, str):
            # 如果是字符串
            d = moment.date(date).format("YYYYM")
            return d
        localdate = timezone.localdate(date)
        logger.info("current local date: %s, date: %s" % (localdate, date))
        return localdate.strftime(cls.DATEFORMAT)


class ModShardMixin(BaseShardMixin):
    """除余分表
    """

    MOD_VALUE = 256
    DEFAULT_TABLE = ""

    @classmethod
    def shard(cls, shard_key=None, mod_value=None, options=None):
        """获取表格
        """
        table_index = cls.__get_table_index(shard_key, mod_value)
        _db_table = "%s_%s" % (cls._meta.db_table, table_index)
        new_model = cls.create_model(table_index)
        ModelSchemaEditor.create_table(new_model)
        return new_model

    @classmethod
    def default_model(cls):
        """默认表格
        """
        default_model = cls.create_model(cls.DEFAULT_TABLE)
        ModelSchemaEditor.create_table(default_model)
        return default_model

    @classmethod
    def get_table_name(cls, shard_key, mod_value=None):
        """获取表格名称
        """
        table_index = cls.__get_table_index(shard_key, mod_value)
        if table_index:
            return "%s_%s" % (cls._meta.db_table, table_index)
        else:
            return cls._meta.db_table

    @classmethod
    def __get_table_index(cls, shard_key, mod_value=None):
        """获取分表索引
        """
        if not mod_value:
            mod_value = cls.MOD_VALUE
        return shard_key % mod_value
