from .admin_repo import AdminRepository
from .ai_requests_repo import AiRequestsRepository
from .days_repo import DaysRepository
from .eating_repo import EatingRepository
from .operations_repo import OperationRepository
from .subscriptions_repo import SubscriptionsRepository
from .users_repo import UserRepository


users_repository = UserRepository()
admin_repository = AdminRepository()
subscriptions_repository = SubscriptionsRepository()
operation_repository = OperationRepository()
eating_repository = EatingRepository()
days_repository = DaysRepository()
ai_requests_repository = AiRequestsRepository()

__all__ = ['users_repository',
           'admin_repository',
           'subscriptions_repository',
           'operation_repository',
           'eating_repository',
           'days_repository',
           'ai_requests_repository'
          ]