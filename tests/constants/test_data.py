"""Уникальные тестовые данные для тестов."""

from __future__ import annotations


class TestUserData:
    """Тестовые данные пользователей."""

    # Базовые пользователи
    OWNER_EMAIL = "owner@example.com"
    OWNER_FULL_NAME = "Owner"
    OWNER_PASSWORD = "Password123!"

    ADMIN_EMAIL = "admin@example.com"
    ADMIN_FULL_NAME = "Admin"
    ADMIN_PASSWORD = "Password123!"

    USER_EMAIL = "user@example.com"
    USER_FULL_NAME = "User"
    USER_PASSWORD = "Password123!"

    USER1_EMAIL = "user1@example.com"
    USER1_FULL_NAME = "User One"
    USER1_PASSWORD = "Password123!"

    USER2_EMAIL = "user2@example.com"
    USER2_FULL_NAME = "User Two"
    USER2_PASSWORD = "Password123!"

    # Специальные пользователи
    PAY_USER_EMAIL = "pay@example.com"
    PAY_USER_FULL_NAME = "Pay"
    PAY_USER_PASSWORD = "Password123!"

    WEBHOOK_USER_EMAIL = "webhook@example.com"
    WEBHOOK_USER_FULL_NAME = "Webhook User"
    WEBHOOK_USER_PASSWORD = "Password123!"

    WH_USER_EMAIL = "wh@example.com"
    WH_USER_FULL_NAME = "WH"
    WH_USER_PASSWORD = "Password123!"

    FLOW_TEST_EMAIL = "flowtest@example.com"
    FLOW_TEST_FULL_NAME = "Flow Test"
    FLOW_TEST_PASSWORD = "Password123!"

    IDEMPOTENT_EMAIL = "idempotent@example.com"
    IDEMPOTENT_FULL_NAME = "Idempotent"
    IDEMPOTENT_PASSWORD = "Password123!"

    ME_USER_EMAIL = "me@example.com"
    ME_USER_FULL_NAME = "Me User"
    ME_USER_PASSWORD = "Password123!"

    JOHN_EMAIL = "john@example.com"
    JOHN_FULL_NAME = "John"
    JOHN_PASSWORD = "Password123!"

    NEW_USER_EMAIL = "newuser@example.com"
    NEW_USER_FULL_NAME = "New User"
    NEW_USER_PASSWORD = "Password123!"

    EXISTING_EMAIL = "existing@example.com"
    EXISTING_FULL_NAME = "Existing"
    EXISTING_PASSWORD = "Password123!"

    ORIGINAL_NAME = "Original Name"
    UPDATED_NAME = "Updated Name"
    JOHNNY_NAME = "Johnny"

    # Неверные данные
    WRONG_EMAIL = "wrong@example.com"
    WRONG_PASSWORD = "wrongpassword"
    NONEXISTENT_EMAIL = "nonexistent@example.com"
    INVALID_EMAIL = "invalid-email"
    EMPTY_EMAIL = ""
    SHORT_PASSWORD = "123"
    INVALID_EMAIL_FORMAT = "invalid-email"
    UNICODE_EMAIL = "пользователь@example.com"
    UNICODE_FULL_NAME = "Иван Петрович Сидоров"
    UNICODE_PASSWORD = "Пароль123!"

    # Тестовые значения для валидации
    TEST_PASSWORD = "pass"
    TEST_PASSWORD_ALT = "password123!"
    TEST_PASSWORD_NEW = "NewPassword123!"
    TEST_EMAIL_UPPER = "USER@EXAMPLE.COM"
    TEST_EMAIL_GENERIC = "test@example.com"
    TEST_NAME_DUPLICATE = "Duplicate"

    # Тестовые значения для core модулей
    TEST_PASSWORD_STRONG = "StrongPassw0rd!"
    TEST_SECRET = "secret"
    TEST_HASHED_PASSWORD = "hash"
    WRONG_PASSWORD_SHORT = "wrong"
    JWT_SECRET_1 = "secret1"
    JWT_SECRET_2 = "secret2"
    WEBHOOK_SECRET_1 = "webhook1"
    PASSWORD_123_STRONG = "Password123!"
    PASSWORD_LOWER_123 = "password123"
    PASS_123 = "Pass123!"
    PASS_456 = "Pass456!"
    NEW_PASS_123 = "NewPass123!"
    SECURE_PASSWORD_123 = "SecurePassword123!"
    PASSWORD_SIMPLE = "password123"
    JWT_TOKEN_EXAMPLE = "jwt.token.here"
    TOKEN_TYPE_CUSTOM = "custom"
    FULL_NAME_WITH_SPACES = "  Test   User  "
    FULL_NAME_UNICODE_RU = "Тестовый Пользователь"
    SPECIAL_PASSWORD_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    NEW_EMAIL_GENERIC = "new@example.com"
    EMAIL_WITH_SPACES = "  test@example.com  "
    LONG_NAME_500_A = "A" * 500
    LONG_EMAIL_LOCAL_A200_EXAMPLE_COM = "a" * 200 + "@example.com"
    JOHNNY_EMAIL = "johnny@example.com"
    LONG_NAME_200_A = "A" * 200
    LONG_NAME_1000_A = "A" * 1000
    LONG_EMAIL_LOCAL_A100_EXAMPLE_COM = "a" * 100 + "@example.com"
    LONG_EMAIL_MAX_LOCAL_EXAMPLE = "a" * 300 + "@example.com"
    ADMIN_USER_PUBLIC_NAME = "Admin User"
    NEW_NAME = "New Name"

    # Unicode и спецсимволы для моделей
    USER_EMAIL_UNICODE_RU = "тест@пример.рф"
    FULL_NAME_UNICODE_MIXED = "Тестовый Пользователь 测试用户"
    HASHED_PASSWORD_UNICODE = "хешированный_пароль"
    EMAIL_WITH_TAG = "test+tag@example.com"
    FULL_NAME_WITH_PUNCT = "O'Connor & Sons, LLC."
    HASHED_PASSWORD_WITH_SPECIALS = "hash!@#$%^&*()"

    # Тестовые значения для конфигурации
    TEST_APP_NAME = "BalanceHub"
    TEST_JWT_ALGORITHM = "HS256"
    TEST_WEBHOOK_SECRET = "test_webhook"
    JWT_SECRET_TEST = "test_secret"
    JWT_SECRET_DEV = "dev_secret"
    JWT_SECRET_PROD = "production_secret"
    WEBHOOK_SECRET_DEV = "dev_webhook"
    WEBHOOK_SECRET_PROD = "production_webhook"

    # Emails/имена для сервисных тестов (accounts/users)
    PAGINATION_EMAIL = "pagination@example.com"
    PAGINATION_FULL_NAME = "Pagination User"
    DEFAULT_PAGINATION_EMAIL = "default_pagination@example.com"
    DEFAULT_PAGINATION_FULL_NAME = "Default Pagination User"
    CREATE_ACCOUNT_EMAIL = "create_account@example.com"
    CREATE_ACCOUNT_FULL_NAME = "Create Account User"
    MULTIPLE_ACCOUNTS_EMAIL = "multiple_accounts@example.com"
    MULTIPLE_ACCOUNTS_FULL_NAME = "Multiple Accounts User"
    GETBYID_EMAIL = "getbyid@example.com"
    GETBYID_FULL_NAME = "Get By ID User"
    UPDATE_EMAIL = "update@example.com"
    UPDATE_FULL_NAME = "Update User"
    OLD_EMAIL = "oldemail@example.com"
    NEW_EMAIL = "newemail@example.com"
    EMAIL_CHANGE_FULL_NAME = "Email Change User"
    PARTIAL_EMAIL = "partial@example.com"
    PARTIAL_FULL_NAME = "Partial Update User"
    DELETE_EMAIL = "delete@example.com"
    DELETE_FULL_NAME = "Delete User"

    # Emails/имена для webhook/прочих тестов
    TOPUP_EMAIL = "topup@example.com"
    TOPUP_FULL_NAME = "Topup"
    NEED_EMAIL = "need@example.com"
    NEED_FULL_NAME = "Need"
    EXISTING_EMAIL_2 = "existing@example.com"
    EXISTING_FULL_NAME_2 = "Existing"
    SMALL_EMAIL = "small@example.com"
    SMALL_FULL_NAME = "Small"
    LARGE_EMAIL = "large@example.com"
    LARGE_FULL_NAME = "Large"
    LARGE_EMAIL_PASSWORD = "Pass123!"
    PRECISE_EMAIL = "precise@example.com"
    PRECISE_FULL_NAME = "Precise"
    NOACCOUNT_EMAIL = "noaccnt@example.com"
    NOACCOUNT_FULL_NAME = "No Account"
    ZERO_EMAIL = "zero@example.com"
    ZERO_FULL_NAME = "Zero"
    PAYMENT_EMAIL = "payment@example.com"
    PAYMENT_FULL_NAME = "Payment"
    ROLLBACK_EMAIL = "rollback@example.com"
    ROLLBACK_FULL_NAME = "Rollback"
    BALANCE_EMAIL = "balance@example.com"
    BALANCE_FULL_NAME = "Balance"

    # Emails/имена для performance тестов
    WEBHOOK_USER_EMAIL = "webhook@example.com"
    WEBHOOK_USER_FULL_NAME = "Webhook User"
    WEBHOOK_USER_PASSWORD = "Pass123!"

    RAPID_EMAIL = "rapid@example.com"
    RAPID_FULL_NAME = "Rapid User"
    RAPID_PASSWORD = "Pass123!"

    STRESS_EMAIL = "stress@example.com"
    STRESS_FULL_NAME = "Stress User"
    STRESS_PASSWORD = "Pass123!"

    TOKEN_STRESS_EMAIL = "token_stress@example.com"
    TOKEN_STRESS_FULL_NAME = "Token Stress"
    TOKEN_STRESS_PASSWORD = "Pass123!"

    POOL_EMAIL = "pool@example.com"
    POOL_FULL_NAME = "Pool User"
    POOL_PASSWORD = "Pass123!"

    PRECISE_EMAIL = "precise@example.com"
    PRECISE_FULL_NAME = "Precise User"
    PRECISE_PASSWORD = "Pass123!"

    # Наборы для создания пользователей без динамики
    BATCH_EMAILS_ABC = (
        "userA@example.com",
        "userB@example.com",
        "userC@example.com",
    )
    BATCH_FULL_NAMES_ABC = ("User A", "User B", "User C")
    PAGINATED_EMAILS_ABCDE = (
        "paginatedA@example.com",
        "paginatedB@example.com",
        "paginatedC@example.com",
        "paginatedD@example.com",
        "paginatedE@example.com",
    )
    PAGINATED_FULL_NAMES_ABCDE = (
        "Paginated User A",
        "Paginated User B",
        "Paginated User C",
        "Paginated User D",
        "Paginated User E",
    )
    FIRST_USER = "First User"
    SECOND_USER = "Second User"

    # Константы для интеграционных тестов
    INTEGRATION_EMAIL = "integration@example.com"
    INTEGRATION_FULL_NAME = "Integration Test User"
    INTEGRATION_PASSWORD = "SecurePass123!"
    INTEGRATION_UPDATED_NAME = "Updated Integration User"

    MULTI_ADMIN_EMAIL = "multiadmin@example.com"
    MULTI_ADMIN_FULL_NAME = "Multi Admin"

    MULTI_USER1_EMAIL = "user1@example.com"
    MULTI_USER1_FULL_NAME = "User One"
    MULTI_USER2_EMAIL = "user2@example.com"
    MULTI_USER2_FULL_NAME = "User Two"
    MULTI_USER3_EMAIL = "user3@example.com"
    MULTI_USER3_FULL_NAME = "User Three"

    ERROR_ADMIN_EMAIL = "erroradmin@example.com"
    ERROR_ADMIN_FULL_NAME = "Error Admin"

    DUPLICATE_EMAIL = "duplicate@example.com"
    DUPLICATE_FULL_NAME = "First User"

    RECOVERY_EMAIL = "recovery@example.com"
    RECOVERY_FULL_NAME = "Recovery User"

    REGULAR_EMAIL = "regular@example.com"
    REGULAR_FULL_NAME = "Regular User"


class TestDomainIds:
    """ID доменных сущностей для тестов."""

    # ID для тестовых случаев
    NONEXISTENT_USER_ID = 999999
    NONEXISTENT_ACCOUNT_ID = 999999
    TEST_USER_ID = 1
    TEST_USER_ID_NEXT = TEST_USER_ID + 1
    TEST_ACCOUNT_ID = 0
    TEST_ACCOUNT_ID_NEXT = TEST_ACCOUNT_ID + 1

    # Строковые ID для тестирования
    STR_ACC_ID_123 = "123"
    STR_USER_ID_456 = "456"

    # Длинные ID для тестирования граничных случаев
    LONG_TX_ID = "transaction-" + "x" * 1000

    # Базовые ID транзакций
    WEBHOOK_TX_1 = "webhook-tx-1"
    TEST_TX_1 = "test-tx-1"
    TEST_TX_2 = "test-tx-2"
    TEST_TX_NEGATIVE = "test-tx-negative"
    TEST_TX_ZERO = "test-tx-zero"
    INTEGRATION_TEST_TX_1 = "integration-test-tx-1"
    IDEMPOTENT_TX_UNIQUE = "idempotent-tx-unique"
    TX_UNIQUE = "tx-unique"
    TX_NEW_ACCOUNT = "tx-new-account"
    TX_EXISTING_ACCOUNT = "tx-existing-account"
    TX_MISMATCH = "tx-mismatch"
    TX_SMALL = "tx-small"
    TX_PRECISE = "tx-precise"
    TX_CREATE_ACCOUNT = "tx-create-account"
    TX_EXISTING_ACCOUNT_DUP = "tx-existing-account"
    TX_BALANCE_1 = "tx-balance-1"
    TX_BALANCE_2 = "tx-balance-2"
    TX_PRECISION = "tx-precision"
    TX_PAYMENT_RECORD = "tx-payment-record"
    UNIQUE_GLOBAL_TX = "unique-global-tx"
    DUPLICATE_TX = "duplicate-tx"
    TX_ZERO = "tx-zero"
    TX_BIG = "tx-big"

    # Специальные ID для тестирования
    TX_NEGATIVE_IDS = "tx-negative-ids"
    TX_LARGE_IDS = "tx-large-ids"
    UNIQUE_TX_1 = "unique-tx-1"
    UNIQUE_TX_2 = "unique-tx-2"
    SPECIAL_CHARS_TX_ID = "tx-!@#$%^&*()_+-=[]{}|;:,.<>?"
    UNICODE_TX_ID = "транзакция-测试-🔥"
    TX_123 = "tx-123"
    TX_STRING = "tx-string"
    TX_MISSING = "tx-missing"
    TX_LONG_SIG = "tx-long-sig"
    TX_UNICODE_SIG = "tx-unicode-sig"
    TX_HEX_SIG = "tx-hex-sig"
    TX_NEGATIVE_ACC = "tx-negative-acc"
    TX_ZERO_ACC = "tx-zero-acc"
    TX_STRING_IDS = "tx-string-ids"
    TX_FLOAT = "tx-float"
    TX_INT = "tx-int"
    TX_NO_SIG = "tx-no-sig"
    TX_SPECIAL = "tx-!@#$%^&*()_+"
    TX_UNICODE_RU = "транзакция-тест"

    # Очень длинные ID для тестирования граничных случаев
    VERY_LONG_TRANSACTION_ID = (
        "very-long-transaction-id-very-long-transaction-id-very-long-transaction-id-"
        "very-long-transaction-id-very-long-transaction-id-very-long-transaction-id-"
        "very-long-transaction-id-very-long-transaction-id-very-long-transaction-id-"
        "very-long-transaction-id-very-long-transaction-id-"
    )

    # Константы для интеграционных тестов
    INTEGRATION_TX_001 = "integration-tx-001"
    INTEGRATION_TX_002 = "integration-tx-002"
    MULTI_TX_001 = "multi-tx-001"
    MULTI_TX_002 = "multi-tx-002"
    MULTI_TX_003 = "multi-tx-003"
    INVALID_SIG_TX = "invalid-sig-tx"


class TestTransactionData:
    """Тестовые данные транзакций."""

    # Неверные/прочие подписи/секреты
    INVALID_SIGNATURE = "invalid_signature"
    EMPTY_SIGNATURE = ""
    TEST_SIGNATURE = "test"
    SECRET_KEY = "key"
    SECRET_KEY_1 = "key1"
    SECRET_KEY_2 = "key2"
    SECRET_UNICODE_RU = "секрет"
    SECRET_SPECIAL = 'key-{}[]|\\;:"<>?'
    SECRET_LONG = (
        "very-long-secret-key-very-long-secret-key-very-long-secret-key-"
        "very-long-secret-key-very-long-secret-key-very-long-secret-key-"
        "very-long-secret-key-very-long-secret-key-very-long-secret-key-"
        "very-long-secret-key-very-long-secret-key-"
    )
    SIGNATURE_VALID = "valid_signature_hash"
    SIGNATURE_GENERIC = "signature"
    LONG_SIGNATURE = "sig-" + "x" * 1000
    UNICODE_SIGNATURE = "подпись-签名-🔐"
    HEX_SIGNATURE_EXAMPLE = "a1b2c3d4e5f6" * 10 + "abcd"


class TestAuthData:
    """Тестовые данные аутентификации."""

    # Токены
    INVALID_JWT = "invalid.jwt"
    INVALID_TOKEN = "invalid.token.here"
    EXPIRED_TOKEN = "expired.token.here"
    INVALID_FORMAT = "InvalidFormat"

    # Заголовки
    BEARER_PREFIX = "Bearer "
    AUTHORIZATION_HEADER = "Authorization"
    CONTENT_TYPE_HEADER = "Content-Type"
    APPLICATION_JSON = "application/json"

    # Типы токенов
    TOKEN_TYPE = "bearer"

    # Неверные заголовки
    MALFORMED_AUTH = "InvalidFormat"
    MISSING_BEARER = "some.jwt.token"


class TestValidationData:
    """Тестовые данные для валидации."""

    # Неверные значения
    NONE_VALUE = None
    EMPTY_STRING = ""
    EXTRA_FIELD = "should_be_ignored"

    # Неверный JSON
    INVALID_JSON = "invalid json"

    # Тестовые значения для обновления
    TEST_FULL_NAME = "Test"
    TEST_USER_FULL_NAME = "Test User"

    # Специальные значения для тестов core
    SPECIAL_CHARS_MESSAGE = "Error with special chars: !@#$%^&*()"
    INVALID_SUBJECT_STR = "not-a-number"
    USER_NOT_FOUND_EN = "User not found"
    ACCESS_DENIED_EN = "Access denied"
    INVALID_CREDENTIALS_EN = "Invalid credentials"
    INVALID_DATA_EN = "Invalid data"
    DB_UNAVAILABLE_EN = "Database unavailable"
    NOT_FOUND_RU = "Пользователь не найден"
    ROOT_CAUSE_MESSAGE = "Root cause"
    VALIDATION_FAILED_MESSAGE = "Validation failed"
    CUSTOM_ERROR_MESSAGE = "Custom error message"
    LETTER_A = "A"
    ERROR_SIMPLE_RU = "Произошла ошибка"
    LONG_ERROR_MESSAGE = "Error: " + "x" * 10000
    UNICODE_ERROR_RU_CN = "Ошибка: пользователь не найден 错误"
    SPECIAL_CHARS_GENERIC = "Error!@#$%^&*()_+-=[]{}|;:,.<>?"
    MULTILINE_MESSAGE = "Line 1\nLine 2\nLine 3"
    HTML_SNIPPET = '<script>alert("xss")</script> Error occurred'
    JSON_STRING = '{"error": "invalid", "code": 400}'
    ORIGIN_EXAMPLE = "https://example.com"
    ORIGIN_TEST = "https://test.com"
    ORIGIN_API = "https://api.com"
    ORIGINS_WITH_SPACES = " https://example.com , https://test.com , "
    ORIGINS_WITH_EMPTY = "https://example.com,,https://test.com,"
    CORS_WILDCARD = "*"


class TestEnvData:
    """Стандартизированные значения окружения для тестов."""

    # БД: драйверы и креды
    DB_ASYNC_DRIVER = "postgresql+asyncpg"
    DB_SYNC_DRIVER = "postgresql+psycopg2"
    DB_USER = "u"
    DB_PASSWORD = "p"
    DB_HOST = "h"
    DB_PORT = "5432"
    DB_NAME = "db"

    # Готовые URL
    SQLITE_MEMORY_URL = "sqlite+aiosqlite:///:memory:"
    POSTGRES_PROD_URL = "postgresql+asyncpg://user:pass@localhost/db"

    # Имена окружений
    ENV_PRODUCTION = "production"
    ENV_DEVELOPMENT = "development"
    DEBUG_TRUE = "true"
    DEBUG_FALSE = "false"
    ENV_FILES = (".env", ".env.local", ".env.docker")


class TestEnvKeys:
    """Имена переменных окружения для тестов."""

    DATABASE_URL = "DATABASE_URL"
    SYNC_DATABASE_URL = "SYNC_DATABASE_URL"
    DB_ASYNC_DRIVER = "DB_ASYNC_DRIVER"
    DB_SYNC_DRIVER = "DB_SYNC_DRIVER"
    DB_USER = "DB_USER"
    DB_PASSWORD = "DB_PASSWORD"
    DB_HOST = "DB_HOST"
    DB_PORT = "DB_PORT"
    DB_NAME = "DB_NAME"
    JWT_SECRET = "JWT_SECRET"
    WEBHOOK_SECRET_KEY = "WEBHOOK_SECRET_KEY"
    CORS_ORIGINS = "CORS_ORIGINS"
    ENV = "ENV"
    DEBUG = "DEBUG"
    PREFIXES = (
        "DB_",
        "DATABASE_",
        "JWT_",
        "WEBHOOK_",
        "CORS_",
        "DEBUG",
        "ENV",
    )
