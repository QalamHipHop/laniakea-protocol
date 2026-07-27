"""
Social Hub API
==============

Provides the social-broadcast surface that the cosmic dashboard uses:
    GET  /social/posts           -> list of recent transmissions
    POST /social/posts           -> publish a new transmission
    GET  /social/feed            -> ordered feed (alias)
    POST /social/follow          -> follow another SCDA
    GET  /social/followers/{id}  -> list followers
    GET  /social/profile/{id}    -> mini social profile
    GET  /social/leaderboard     -> most-followed SCDAs
    GET  /social/stats           -> hub stats

The router is intentionally in-memory so it has zero external dependencies
and works in any environment (Render, local, CI).
"""

from __future__ import annotations

import logging
import time as _t
import uuid
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["Social Hub"])

# In-memory state ----------------------------------------------------
_MAX_POSTS = 500
_posts: Deque[Dict[str, Any]] = deque(maxlen=_MAX_POSTS)
_followers: Dict[str, set] = defaultdict(set)  # followee -> {follower ids}
_profiles: Dict[str, Dict[str, Any]] = {}

# Pydantic schemas ----------------------------------------------------
class PostCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="cosmos", max_length=40)


class FollowRequest(BaseModel):
    follower: str = Field(..., min_length=1)
    followee: str = Field(..., min_length=1)


# Helpers -------------------------------------------------------------
def _ensure_profile(scda_id: str) -> Dict[str, Any]:
    prof = _profiles.get(scda_id)
    if not prof:
        prof = {
            "scda_id": scda_id,
            "username": scda_id,
            "tier": "A",
            "bio": f"Cosmic identity {scda_id}",
            "joined_at": _t.time(),
            "post_count": 0,
        }
        _profiles[scda_id] = prof
    return prof


def _serialize_post(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": p["id"],
        "author": p["author"],
        "content": p["content"],
        "channel": p.get("channel", "cosmos"),
        "timestamp": p["timestamp"],
        "likes": p.get("likes", 0),
    }


# Routes --------------------------------------------------------------
@router.get("/posts", summary="List recent social posts")
def list_posts(limit: int = 50) -> Dict[str, Any]:
    items = [_serialize_post(p) for p in list(_posts)[-limit:][::-1]]
    return {"posts": items, "count": len(items)}


@router.get("/feed", summary="Alias for /social/posts")
def feed(limit: int = 50) -> Dict[str, Any]:
    return list_posts(limit=limit)


@router.post("/posts", status_code=201, summary="Publish a new post")
def create_post(payload: PostCreate) -> Dict[str, Any]:
    post = {
        "id": uuid.uuid4().hex[:12],
        "author": payload.author,
        "content": payload.content,
        "channel": payload.channel,
        "timestamp": _t.time(),
        "likes": 0,
    }
    _posts.append(post)
    prof = _ensure_profile(payload.author)
    prof["post_count"] = prof.get("post_count", 0) + 1
    logger.info("Social post by %s on #%s (%d chars)", payload.author, payload.channel, len(payload.content))
    return _serialize_post(post)


@router.post("/follow", summary="Follow another SCDA")
def follow(payload: FollowRequest) -> Dict[str, Any]:
    if payload.follower == payload.followee:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    _ensure_profile(payload.follower)
    _ensure_profile(payload.followee)
    _followers[payload.followee].add(payload.follower)
    return {
        "follower": payload.follower,
        "followee": payload.followee,
        "followers_count": len(_followers[payload.followee]),
    }


@router.delete("/follow", summary="Unfollow")
def unfollow(payload: FollowRequest) -> Dict[str, Any]:
    if payload.follower in _followers.get(payload.followee, set()):
        _followers[payload.followee].discard(payload.follower)
    return {"follower": payload.follower, "followee": payload.followee, "ok": True}


@router.get("/followers/{scda_id}", summary="List followers of an SCDA")
def followers(scda_id: str) -> Dict[str, Any]:
    return {
        "scda_id": scda_id,
        "followers": sorted(_followers.get(scda_id, set())),
        "count": len(_followers.get(scda_id, set())),
    }


@router.get("/profile/{scda_id}", summary="Mini social profile")
def profile(scda_id: str) -> Dict[str, Any]:
    prof = _ensure_profile(scda_id)
    return {
        **prof,
        "followers": len(_followers.get(scda_id, set())),
        "following": sum(1 for f in _followers.values() if scda_id in f),
    }


@router.get("/leaderboard", summary="Most-followed SCDAs")
def leaderboard(top: int = 10) -> List[Dict[str, Any]]:
    items = [
        {"scda_id": sid, "followers": len(followers)}
        for sid, followers in _followers.items()
        if followers
    ]
    items.sort(key=lambda x: x["followers"], reverse=True)
    return items[:top]


@router.get("/stats", summary="Social hub stats")
def stats() -> Dict[str, Any]:
    total_follows = sum(len(s) for s in _followers.values())
    return {
        "posts": len(_posts),
        "identities_seen": len(_profiles),
        "follow_relations": total_follows,
        "max_capacity": _MAX_POSTS,
    }


# --------------------------------------------------------------------
# Backwards-compatible aliases (some UIs may call /social/post singular)
# --------------------------------------------------------------------
@router.post("/post", status_code=201, include_in_schema=False)
def _legacy_create_post(payload: PostCreate) -> Dict[str, Any]:
    return create_post(payload)


@router.get("/post", include_in_schema=False)
def _legacy_list_posts(limit: int = 50) -> Dict[str, Any]:
    return list_posts(limit=limit)
