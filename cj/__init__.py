import typing
import inspect
from collections import defaultdict, namedtuple

from pkg_resources import DistributionNotFound, get_distribution

from ._compat import is_generic_list, ensure_forward_ref

try:  # pragma no cover
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma no cover
    pass


class MissingDependencyException(Exception):
    pass

class InvalidRegistrationException(Exception):
    pass

class InvalidForwardReferenceException(Exception):
    pass

Registration = namedtuple("Registration", ["service", "builder", "needs", "args"])

class Empty:
    pass

empty = Empty()

class Registry:
    def __init__(self):
        self.__registrations = defaultdict(list)
        self._localns = dict()

    def _get_needs_for_ctor(self, cls):
        try:
            return typing.get_type_hints(cls.__init__, None, self._localns)
        except NameError as e:
            raise InvalidForwardReferenceException(str(e))

    def register_service_and_impl(self, service, impl, resolve_args):
        self.__registrations[service].append(
            Registration(service, impl, self._get_needs_for_ctor(impl), resolve_args)
        )

    def register_service_and_instance(self, service, instance):
        self.__registrations[service].append(
            Registration(service, lambda: instance, {}, {})
        )

    def register_concrete_service(self, service):
        if not type(service) is type:
            raise InvalidRegistrationException(
                "El servicio %s no puede ser registrado como su propia implementacion"
                % (repr(service))
            )
        self.__registrations[service].append(
            Registration(service, service, self._get_needs_for_ctor(service), {})
        )

    def build_context(self, key, existing=None):
        if existing is None:
            return ResolutionContext(key, list(self.__getitem__(key)))

        if key not in existing.targets:
            existing.targets[key] = ResolutionTarget(key, list(self.__getitem__(key)))

        return existing

    def _update_localns(self, service):
        if type(service) == type:
            self._localns[service.__name__] = service
        else:
            self._localns[service] = service

    def register(self, service, factory=empty, instance=empty, **kwargs):
        resolve_args = kwargs or {}

        if instance is not empty:
            self.register_service_and_instance(service, instance)
        elif factory is empty:
            self.register_concrete_service(service)
        elif callable(factory):
            self.register_service_and_impl(service, factory, resolve_args)
        else:
            raise InvalidRegistrationException(
                f"Se esperaba callable factory para el servicio {service} pero se recibio {factory}"
            )
        self._update_localns(service)
        ensure_forward_ref(self, service, factory, instance, **kwargs)

    def __getitem__(self, service):
        return self.__registrations[service]

class ResolutionTarget:
    def __init__(self, key, impls):
        self.service = key
        self.impls = impls

    def is_generic_list(self):
        return is_generic_list(self.service)

    @property
    def generic_parameter(self):
        return self.service.__args__[0]

    def next_impl(self):
        if len(self.impls) > 0:
            return self.impls.pop()

class ResolutionContext:
    def __init__(self, key, impls):
        self.targets = {key: ResolutionTarget(key, impls)}
        self.cache = {}
        self.service = key

    def target(self, key):
        return self.targets.get(key)

    def has_cached(self, key):
        return key in self.cache

    def __getitem__(self, key):
        return self.cache.get(key)

    def __setitem__(self, key, instance):
        self.cache[key] = instance

    def all_registrations(self, service):
        return self.targets[service].impls

class Container:

    def __init__(self):
        self.registrations = Registry()

    def register(self, service, factory=empty, instance=empty, **kwargs):
        self.registrations.register(service, factory, instance, **kwargs)
        return self

    def resolve_all(self, service, **kwargs):
        context = self.registrations.build_context(service)

        return [
            self._build_impl(x, kwargs, context)
            for x in context.all_registrations(service)
        ]

    def _build_impl(self, registration, resolution_args, context):

        args = {
            k: self._resolve_impl(v, resolution_args, context)
            for k, v in registration.needs.items()
            if k != "return" and k not in registration.args and k not in resolution_args
        }
        args.update(registration.args)

        target_args = inspect.getfullargspec(registration.builder).args
        if "self" in target_args:
            target_args.remove("self")
        condensed_resolution_args = {
            key: resolution_args[key] for key in resolution_args if key in target_args
        }
        args.update(condensed_resolution_args or {})

        result = registration.builder(**args)
        context[registration.service] = result

        return result

    def _resolve_impl(self, service_key, kwargs, context):

        context = self.registrations.build_context(service_key, context)

        if context.has_cached(service_key):
            return context[service_key]

        target = context.target(service_key)

        if target.is_generic_list():
            return self.resolve_all(target.generic_parameter)

        registration = target.next_impl()

        if registration is None:
            raise MissingDependencyException(
                "Error al resolver la implementacion para " + str(service_key)
            )

        if service_key in registration.needs.values():
            self._resolve_impl(service_key, kwargs, context)

        return self._build_impl(registration, kwargs, context)

    def resolve(self, service_key, **kwargs):
        context = self.registrations.build_context(service_key)

        return self._resolve_impl(service_key, kwargs, context)
