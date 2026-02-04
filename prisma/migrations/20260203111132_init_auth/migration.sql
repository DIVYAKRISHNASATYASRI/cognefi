-- CreateTable
CREATE TABLE "Tenant" (
    "tenant_id" UUID NOT NULL,
    "tenant_name" TEXT NOT NULL,
    "tenant_code" TEXT NOT NULL,
    "industry" TEXT,
    "subscription_plan" TEXT NOT NULL DEFAULT 'free',
    "status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Tenant_pkey" PRIMARY KEY ("tenant_id")
);

-- CreateTable
CREATE TABLE "UserProfile" (
    "user_id" UUID NOT NULL,
    "tenant_id" UUID,
    "clerk_user_id" TEXT,
    "full_name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "role" TEXT NOT NULL DEFAULT 'USER',
    "status" TEXT NOT NULL DEFAULT 'active',
    "permissions" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "UserProfile_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "AuthToken" (
    "token_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "token_type" TEXT NOT NULL,
    "token_hash" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "used_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AuthToken_pkey" PRIMARY KEY ("token_id")
);

-- CreateTable
CREATE TABLE "LoginOTP" (
    "otp_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "otp_code" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "verified_at" TIMESTAMP(3),
    "ip_address" TEXT,
    "user_agent" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "LoginOTP_pkey" PRIMARY KEY ("otp_id")
);

-- CreateTable
CREATE TABLE "AuthAuditLog" (
    "log_id" UUID NOT NULL,
    "user_id" UUID,
    "event_type" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AuthAuditLog_pkey" PRIMARY KEY ("log_id")
);

-- CreateTable
CREATE TABLE "Agent" (
    "agent_id" UUID NOT NULL,
    "tenant_id" UUID,
    "created_by" UUID NOT NULL,
    "agent_name" TEXT NOT NULL,
    "description" TEXT,
    "status" TEXT NOT NULL DEFAULT 'active',
    "access_type" TEXT NOT NULL DEFAULT 'PRIVATE',
    "is_public" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "Agent_pkey" PRIMARY KEY ("agent_id")
);

-- CreateTable
CREATE TABLE "AgentSubscription" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "agent_id" UUID NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AgentSubscription_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentModelConfig" (
    "id" UUID NOT NULL,
    "agent_id" UUID NOT NULL,
    "model_provider" TEXT NOT NULL DEFAULT 'openai',
    "model_name" TEXT NOT NULL DEFAULT 'gpt-4o',
    "temperature" DOUBLE PRECISION NOT NULL DEFAULT 0.7,

    CONSTRAINT "AgentModelConfig_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentPrompt" (
    "id" UUID NOT NULL,
    "agent_id" UUID NOT NULL,
    "instructions" TEXT,
    "system_message" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "AgentPrompt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentMemoryConfig" (
    "id" UUID NOT NULL,
    "agent_id" UUID NOT NULL,
    "enable_agentic_memory" BOOLEAN NOT NULL DEFAULT false,
    "num_history_runs" INTEGER NOT NULL DEFAULT 3,

    CONSTRAINT "AgentMemoryConfig_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentOpsConfig" (
    "id" UUID NOT NULL,
    "agent_id" UUID NOT NULL,
    "markdown" BOOLEAN NOT NULL DEFAULT true,
    "output_schema" TEXT,

    CONSTRAINT "AgentOpsConfig_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentSession" (
    "session_id" TEXT NOT NULL,
    "agent_id" UUID NOT NULL,
    "start_time" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" TEXT NOT NULL DEFAULT 'running',

    CONSTRAINT "AgentSession_pkey" PRIMARY KEY ("session_id")
);

-- CreateTable
CREATE TABLE "AgentOutput" (
    "output_id" UUID NOT NULL,
    "session_id" TEXT NOT NULL,
    "input_payload" TEXT NOT NULL,
    "raw_response" JSONB,
    "output_schema" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AgentOutput_pkey" PRIMARY KEY ("output_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Tenant_tenant_code_key" ON "Tenant"("tenant_code");

-- CreateIndex
CREATE UNIQUE INDEX "UserProfile_clerk_user_id_key" ON "UserProfile"("clerk_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "UserProfile_email_key" ON "UserProfile"("email");

-- CreateIndex
CREATE UNIQUE INDEX "AuthToken_token_hash_key" ON "AuthToken"("token_hash");

-- CreateIndex
CREATE INDEX "AuthToken_token_hash_idx" ON "AuthToken"("token_hash");

-- CreateIndex
CREATE INDEX "AuthToken_user_id_idx" ON "AuthToken"("user_id");

-- CreateIndex
CREATE INDEX "LoginOTP_user_id_created_at_idx" ON "LoginOTP"("user_id", "created_at");

-- CreateIndex
CREATE INDEX "AuthAuditLog_user_id_created_at_idx" ON "AuthAuditLog"("user_id", "created_at");

-- CreateIndex
CREATE INDEX "AuthAuditLog_event_type_idx" ON "AuthAuditLog"("event_type");

-- CreateIndex
CREATE UNIQUE INDEX "AgentSubscription_user_id_agent_id_key" ON "AgentSubscription"("user_id", "agent_id");

-- CreateIndex
CREATE UNIQUE INDEX "AgentModelConfig_agent_id_key" ON "AgentModelConfig"("agent_id");

-- CreateIndex
CREATE UNIQUE INDEX "AgentMemoryConfig_agent_id_key" ON "AgentMemoryConfig"("agent_id");

-- CreateIndex
CREATE UNIQUE INDEX "AgentOpsConfig_agent_id_key" ON "AgentOpsConfig"("agent_id");

-- AddForeignKey
ALTER TABLE "UserProfile" ADD CONSTRAINT "UserProfile_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "Tenant"("tenant_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AuthToken" ADD CONSTRAINT "AuthToken_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "UserProfile"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LoginOTP" ADD CONSTRAINT "LoginOTP_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "UserProfile"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AuthAuditLog" ADD CONSTRAINT "AuthAuditLog_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "UserProfile"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Agent" ADD CONSTRAINT "Agent_tenant_id_fkey" FOREIGN KEY ("tenant_id") REFERENCES "Tenant"("tenant_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Agent" ADD CONSTRAINT "Agent_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "UserProfile"("user_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentSubscription" ADD CONSTRAINT "AgentSubscription_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "UserProfile"("user_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentSubscription" ADD CONSTRAINT "AgentSubscription_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentModelConfig" ADD CONSTRAINT "AgentModelConfig_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentPrompt" ADD CONSTRAINT "AgentPrompt_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentMemoryConfig" ADD CONSTRAINT "AgentMemoryConfig_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentOpsConfig" ADD CONSTRAINT "AgentOpsConfig_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentSession" ADD CONSTRAINT "AgentSession_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "Agent"("agent_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentOutput" ADD CONSTRAINT "AgentOutput_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "AgentSession"("session_id") ON DELETE CASCADE ON UPDATE CASCADE;
