"""
Tests for session endpoints.
"""

from uuid import uuid4

import pytest

from app.models.session import ChatSession
from app.schemas.session import SessionCreateSchema, SessionSettingsSchema


@pytest.mark.asyncio
async def test_create_session(client, test_user, auth_headers):
    """Test creating a new session."""
    response = await client.post(
        "/api/v1/sessions",
        json={
            "title": "Test Session",
            "agent_type": "react",
            "settings": {
                "temperature": 0.8,
                "max_tokens": 2048,
            },
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "Test Session"
    assert data["data"]["agent_type"] == "react"
    assert data["data"]["settings"]["temperature"] == 0.8


@pytest.mark.asyncio
async def test_list_sessions(client, test_user, auth_headers, db):
    """Test listing user sessions."""
    # Create test sessions
    session1 = ChatSession(
        user_id=test_user.id,
        title="Session 1",
        agent_type="react",
        settings={},
    )
    session2 = ChatSession(
        user_id=test_user.id,
        title="Session 2",
        agent_type="agentic_rag",
        settings={},
    )
    db.add_all([session1, session2])
    await db.commit()

    # List sessions
    response = await client.get("/api/v1/sessions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] >= 2
    assert len(data["data"]["items"]) >= 2


@pytest.mark.asyncio
async def test_get_session(client, test_user, auth_headers, db):
    """Test getting session details."""
    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="Test Session",
        agent_type="react",
        settings={"temperature": 0.7},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Get session
    response = await client.get(f"/api/v1/sessions/{session.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["id"] == str(session.id)
    assert data["data"]["title"] == "Test Session"


@pytest.mark.asyncio
async def test_update_session(client, test_user, auth_headers, db):
    """Test updating a session."""
    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="Old Title",
        agent_type="react",
        settings={},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Update session
    response = await client.put(
        f"/api/v1/sessions/{session.id}",
        json={"title": "New Title"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_session(client, test_user, auth_headers, db):
    """Test deleting a session."""
    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="To Delete",
        agent_type="react",
        settings={},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Delete session
    response = await client.delete(
        f"/api/v1/sessions/{session.id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0

    # Verify soft delete
    await db.refresh(session)
    assert session.is_deleted is True


@pytest.mark.asyncio
async def test_add_message(client, test_user, auth_headers, db):
    """Test adding a message to a session."""
    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="Test Session",
        agent_type="react",
        settings={},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Add message
    response = await client.post(
        f"/api/v1/sessions/{session.id}/messages",
        json={
            "role": "user",
            "content": "Hello, how are you?",
            "meta": {"source": "web"},
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["role"] == "user"
    assert data["data"]["content"] == "Hello, how are you?"
    assert data["data"]["meta"]["source"] == "web"


@pytest.mark.asyncio
async def test_list_messages(client, test_user, auth_headers, db):
    """Test listing messages in a session."""
    from app.models.message import ChatMessage

    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="Test Session",
        agent_type="react",
        settings={},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Create test messages
    msg1 = ChatMessage(
        session_id=session.id,
        role="user",
        content="Hello",
        meta={},
    )
    msg2 = ChatMessage(
        session_id=session.id,
        role="assistant",
        content="Hi there!",
        meta={},
    )
    db.add_all([msg1, msg2])
    await db.commit()

    # List messages
    response = await client.get(
        f"/api/v1/sessions/{session.id}/messages", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_nonexistent_session(client, test_user, auth_headers):
    """Test getting a non-existent session."""
    fake_id = uuid4()
    response = await client.get(f"/api/v1/sessions/{fake_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 40400
    assert "not found" in data["message"].lower()


@pytest.mark.asyncio
async def test_unauthorized_access(client, test_user, db):
    """Test accessing sessions without authentication."""
    # Create test session
    session = ChatSession(
        user_id=test_user.id,
        title="Test Session",
        agent_type="react",
        settings={},
    )
    db.add(session)
    await db.commit()

    # Try to access without auth
    response = await client.get("/api/v1/sessions")
    assert response.status_code == 401
