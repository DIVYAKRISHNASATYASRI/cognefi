import asyncio
from prisma import Json
from app.core.db import db


async def main():
    await db.connect()

    # -------------------------------------------------
    # CLEAN UP (only existing tables, safe order)
    # -------------------------------------------------
    await db.agentsubscription.delete_many()
    await db.agent.delete_many()
    await db.userprofile.delete_many()
    await db.tenant.delete_many()

    # -------------------------------------------------
    # TENANTS
    # -------------------------------------------------
    platform_tenant = await db.tenant.create(
        data={
            "tenant_name": "Cognefi Platform",
            "tenant_code": "COGNEFI_GLOBAL",
            "industry": "AI",
            "subscription_plan": "enterprise",
            "status": "active",
        }
    )

    tenant_a = await db.tenant.create(
        data={
            "tenant_name": "Tenant Alpha",
            "tenant_code": "TENANT_ALPHA",
            "industry": "Finance",
            "subscription_plan": "pro",
            "status": "active",
        }
    )

    tenant_b = await db.tenant.create(
        data={
            "tenant_name": "Tenant Beta",
            "tenant_code": "TENANT_BETA",
            "industry": "Healthcare",
            "subscription_plan": "free",
            "status": "suspended",
        }
    )

    # -------------------------------------------------
    # USERS
    # -------------------------------------------------
    super_admin = await db.userprofile.create(
        data={
            "full_name": "Super Admin",
            "email": "superadmin@cognefi.com",
            "role": "SUPER_ADMIN",
            "status": "active",
            "permissions": Json({"platform": True}),
        }
    )

    tenant_a_admin = await db.userprofile.create(
        data={
            "tenant_id": tenant_a.tenant_id,
            "full_name": "Tenant A Admin",
            "email": "admin@alpha.com",
            "role": "TENANT_ADMIN",
            "status": "active",
            "permissions": Json({"manage_users": True, "manage_agents": True}),
        }
    )

    tenant_a_user = await db.userprofile.create(
        data={
            "tenant_id": tenant_a.tenant_id,
            "full_name": "Tenant A User",
            "email": "user@alpha.com",
            "role": "USER",
            "status": "active",
        }
    )

    tenant_b_admin = await db.userprofile.create(
        data={
            "tenant_id": tenant_b.tenant_id,
            "full_name": "Tenant B Admin",
            "email": "admin@beta.com",
            "role": "TENANT_ADMIN",
            "status": "inactive",
        }
    )

    # -------------------------------------------------
    # AGENTS
    # -------------------------------------------------
    global_agent = await db.agent.create(
        data={
            "agent_name": "Global Market Agent",
            "description": "Global marketplace agent",
            "access_type": "GLOBAL",
            "is_public": True,
            "status": "active",
            "created_by": super_admin.user_id,
        }
    )

    tenant_a_private_agent = await db.agent.create(
        data={
            "agent_name": "Tenant A Private Agent",
            "description": "Private agent for Tenant A",
            "tenant_id": tenant_a.tenant_id,
            "access_type": "PRIVATE",
            "is_public": False,
            "status": "active",
            "created_by": tenant_a_admin.user_id,
        }
    )

    # -------------------------------------------------
    # SUBSCRIPTIONS
    # -------------------------------------------------
    await db.agentsubscription.create(
        data={
            "user_id": tenant_a_admin.user_id,
            "agent_id": global_agent.agent_id,
        }
    )

    await db.agentsubscription.create(
        data={
            "user_id": tenant_a_user.user_id,
            "agent_id": global_agent.agent_id,
        }
    )

    print("\n✅ Cerbos Test Seed Completed Successfully\n")

    print("TENANTS")
    print(" - Platform:", platform_tenant.tenant_id)
    print(" - Tenant A:", tenant_a.tenant_id)
    print(" - Tenant B (suspended):", tenant_b.tenant_id)

    print("\nUSERS")
    print(" - Super Admin:", super_admin.user_id)
    print(" - Tenant A Admin:", tenant_a_admin.user_id)
    print(" - Tenant A User:", tenant_a_user.user_id)
    print(" - Tenant B Admin (inactive):", tenant_b_admin.user_id)

    print("\nAGENTS")
    print(" - Global Agent:", global_agent.agent_id)
    print(" - Tenant A Private Agent:", tenant_a_private_agent.agent_id)

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
