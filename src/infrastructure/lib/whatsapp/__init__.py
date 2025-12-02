from typing import Any, Dict, Optional

import httpx
from decouple import config

from src.infrastructure.lib.whatsapp._schemas import *
from src.infrastructure.lib.whatsapp.decrypt_whatsapp_media import (
    MediaType,
    decrypt_whatsapp_media,
)
from src.infrastructure.lib.whatsapp.download_whatsapp_file import (
    download_whatsapp_file,
)


class WhatsAppApiClient:
    """
    Asynchronous client for interacting with the WAHA - WhatsApp HTTP API.

    Documentation: https://waha.devlike.pro/
    """

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._async_client = httpx.AsyncClient(base_url=self.base_url)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        content: Any = None,
    ) -> httpx.Response:
        """
        Internal method to make asynchronous HTTP requests.
        """
        headers = {"X-Api-Key": self.api_key}
        try:
            response = await self._async_client.request(
                method,
                path,
                params=params,
                json=json_data,
                content=content,
                headers=headers,
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response content: {e}")  # Print response content for debugging
            raise

    async def close(self):
        """
        Closes the underlying httpx AsyncClient session.
        """
        await self._async_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # 🔑 Auth Endpoints

    async def get_qr_code(self, session: str, format: str) -> AuthGetQRResponse:
        """
        Get QR code for pairing WhatsApp API.
        """
        path = f"/api/{session}/auth/qr"
        params = {"format": format}
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def request_code(
        self, session: str, request_body: RequestCodeRequest
    ) -> httpx.Response:  # type: ignore[override] # Generic HttpResponse, no typed response
        """
        Request authentication code.
        """
        path = f"/api/{session}/auth/request-code"
        return await self._request("POST", path, json_data=request_body)

    async def authorize_code(
        self, session: str, request_body: OTPRequest
    ) -> httpx.Response:  # type: ignore[override] # Generic HttpResponse, no typed response
        """
        Send OTP authentication code.
        """
        path = f"/api/{session}/auth/authorize-code"
        return await self._request("POST", path, json_data=request_body)

    async def get_captcha(self, session: str) -> AuthGetCaptchaResponse:
        """
        Get captcha image.
        """
        path = f"/api/{session}/auth/captcha"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def save_captcha(
        self, session: str, request_body: CaptchaBody
    ) -> httpx.Response:  # type: ignore[override] # Generic HttpResponse, no typed response
        """
        Enter captcha code.
        """
        path = f"/api/{session}/auth/captcha"
        return await self._request("POST", path, json_data=request_body)

    # 🖥️ Sessions Endpoints

    async def list_sessions(
        self, all_sessions: Optional[bool] = None
    ) -> SessionsListSessionsResponse:
        """
        List all sessions
        """
        path = "/api/sessions"
        params = {"all": all_sessions} if all_sessions is not None else None
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def create_session(
        self, request_body: SessionCreateRequest
    ) -> SessionsCreateSessionResponse:
        """
        Create a session
        """
        path = "/api/sessions"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def get_session_info(self, session: str) -> SessionsGetSessionInfoResponse:
        """
        Get session information
        """
        path = f"/api/sessions/{session}"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def update_session(
        self, session: str, request_body: SessionUpdateRequest
    ) -> SessionsUpdateSessionResponse:
        """
        Update a session
        """
        path = f"/api/sessions/{session}/sessions/{session}"  # corrected path
        response = await self._request("PUT", path, json_data=request_body)
        return response.json()  # type: ignore

    async def delete_session(self, session: str) -> httpx.Response:  # type: ignore[override]
        """
        Delete the session
        """
        path = f"/api/sessions/{session}"
        return await self._request("DELETE", path)

    async def get_me(self, session: str) -> SessionsGetMeResponse:
        """
        Get information about the authenticated account
        """
        path = f"/api/sessions/{session}/me"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def start_session(self, session: str) -> SessionsStartSessionResponse:
        """
        Start the session
        """
        path = f"/api/sessions/{session}/start"
        response = await self._request("POST", path)
        return response.json()  # type: ignore

    async def stop_session(self, session: str) -> SessionsStopSessionResponse:
        """
        Stop the session
        """
        path = f"/api/sessions/{session}/stop"
        response = await self._request("POST", path)
        return response.json()  # type: ignore

    async def logout_session(self, session: str) -> SessionsLogoutSessionResponse:
        """
        Logout from the session
        """
        path = f"/api/sessions/{session}/logout"  # corrected path
        response = await self._request("POST", path)
        return response.json()  # type: ignore

    async def restart_session(self, session: str) -> SessionsRestartSessionResponse:
        """
        Restart the session
        """
        path = f"/api/sessions/{session}/restart"
        response = await self._request("POST", path)
        return response.json()  # type: ignore

    async def deprecated_start_session(
        self, request_body: SessionStartDeprecatedRequest
    ) -> SessionsDeprecatedStartSessionResponse:
        """
        [DEPRECATED] Upsert and Start session
        """
        path = "/api/sessions/start"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def deprecated_stop_session(
        self, request_body: SessionStopDeprecatedRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        [DEPRECATED] Stop (and Logout if asked) session
        """
        path = "/api/sessions/stop"
        return await self._request("POST", path, json_data=request_body)

    async def deprecated_logout_session(
        self, request_body: SessionLogoutDeprecatedRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        [DEPRECATED] Logout and Delete session.
        """
        path = "/api/sessions/logout"
        return await self._request("POST", path, json_data=request_body)

    # 📤 Chatting Endpoints

    async def send_text_message(
        self, request_body: MessageTextRequest
    ) -> ChattingSendTextResponse:
        """
        Send a text message
        """
        path = "/api/sendText"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def deprecated_send_text_message_get(
        self, phone: str, text: str, session: str = "default"
    ) -> httpx.Response:  # type: ignore[override]
        """
        [DEPRECATED] Send a text message (GET method - deprecated)
        """
        path = "/api/sendText"
        params = {"phone": phone, "text": text, "session": session}
        return await self._request("GET", path, params=params)

    async def send_image_message(
        self, request_body: MessageImageRequest
    ) -> ChattingSendImageResponse:
        """
        Send an image
        """
        path = "/api/sendImage"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def send_file_message(
        self, request_body: MessageFileRequest
    ) -> ChattingSendFileResponse:
        """
        Send a file
        """
        path = "/api/sendFile"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def send_voice_message(
        self, request_body: MessageVoiceRequest
    ) -> ChattingSendVoiceResponse:
        """
        Send an voice message
        """
        path = "/api/sendVoice"
        response = await self._request("POST", path, json_data=request_body)
        return response.content  # type: ignore

    async def send_video_message(
        self, request_body: MessageVideoRequest
    ) -> ChattingSendVideoResponse:
        """
        Send a video
        """
        path = "/api/sendVideo"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def send_buttons_message(
        self, request_body: SendButtonsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send buttons (interactive message)
        """
        path = "/api/sendButtons"
        return await self._request("POST", path, json_data=request_body)

    async def forward_message(
        self, request_body: MessageForwardRequest
    ) -> ChattingForwardMessageResponse:
        """
        Forward a message
        """
        path = "/api/forwardMessage"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def send_seen(
        self, request_body: SendSeenRequest
    ) -> ChattingSendSeenResponse:
        """
        Send 'seen' status for a message
        """
        path = "/api/sendSeen"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def start_typing(
        self, session: str, request_body: ChatRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Start typing in a chat
        """
        path = "/api/startTyping"
        return await self._request("POST", path, json_data=request_body)

    async def stop_typing(
        self, session: str, request_body: ChatRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Stop typing in a chat
        """
        path = "/api/stopTyping"
        return await self._request("POST", path, json_data=request_body)

    async def set_reaction(
        self, request_body: MessageReactionRequest
    ) -> ChattingSetReactionResponse:
        """
        React to a message with an emoji
        """
        path = "/api/reaction"
        response = await self._request("PUT", path, json_data=request_body)
        return response.json()  # type: ignore

    async def set_star(self, request_body: MessageStarRequest) -> httpx.Response:  # type: ignore[override]
        """
        Star or unstar a message
        """
        path = "/api/star"
        return await self._request("PUT", path, json_data=request_body)

    async def send_poll_message(
        self, request_body: MessagePollRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send a poll with options
        """
        path = "/api/sendPoll"
        return await self._request("POST", path, json_data=request_body)

    async def send_location_message(
        self, request_body: MessageLocationRequest
    ) -> ChattingSendMessageLocationResponse:
        """
        Send a location message
        """
        path = "/api/sendLocation"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def send_link_preview_message(
        self, request_body: MessageLinkPreviewRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send a link preview message
        """
        path = "/api/sendLinkPreview"
        return await self._request("POST", path, json_data=request_body)

    async def send_contact_vcard_message(
        self, request_body: MessageContactVcardRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send a contact vcard message
        """
        path = "/api/sendContactVcard"
        return await self._request("POST", path, json_data=request_body)

    async def deprecated_get_messages(
        self,
        session: str,
        chatId: str,
        limit: int,
        downloadMedia: Optional[bool] = False,
        offset: Optional[int] = None,
        filter_timestamp_lte: Optional[int] = None,
        filter_timestamp_gte: Optional[int] = None,
        filter_fromMe: Optional[bool] = None,
    ) -> ChattingDeprecatedGetMessagesResponse:
        """
        [DEPRECATED] Get messages in a chat
        """
        path = "/api/messages"
        params = {}
        params["session"] = session
        params["chatId"] = chatId
        params["limit"] = limit
        if downloadMedia is not None:
            params["downloadMedia"] = downloadMedia
        if offset is not None:
            params["offset"] = offset
        if filter_timestamp_lte is not None:
            params["filter.timestamp.lte"] = filter_timestamp_lte
        if filter_timestamp_gte is not None:
            params["filter.timestamp.gte"] = filter_timestamp_gte
        if filter_fromMe is not None:
            params["filter.fromMe"] = filter_fromMe
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def deprecated_check_number_status(
        self, session: str, phone: str
    ) -> ChattingDeprecatedCheckNumberStatusResponse:
        """
        [DEPRECATED] Check number status
        """
        path = "/api/checkNumberStatus"
        params = {"session": session, "phone": phone}
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def deprecated_reply_message(
        self, request_body: MessageReplyRequest
    ) -> ChattingDeprecatedReplyMessageResponse:
        """
        [DEPRECATED] Reply to a message
        """
        path = "/api/reply"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    # 💬 Chats Endpoints

    async def get_chats(
        self,
        session: str,
        sortBy: Optional[str] = None,
        sortOrder: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ChatsGetChatsResponse:
        """
        Get chats
        """
        path = f"/api/{session}/chats"
        params = {}
        if sortBy is not None:
            params["sortBy"] = sortBy
        if sortOrder is not None:
            params["sortOrder"] = sortOrder
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params = params if params else None  # params should be None if empty
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def get_chats_overview(
        self, session: str, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> ChatsGetChatsOverviewResponse:
        """
        Get chats overview.
        """
        path = f"/api/{session}/chats/overview"
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params = params if params else None  # params should be None if empty
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def delete_chat(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Deletes the chat
        """
        path = f"/api/{session}/chats/{chatId}"
        return await self._request("DELETE", path)

    async def get_chat_picture(
        self, session: str, chatId: str, refresh: Optional[bool] = None
    ) -> ChatsGetChatPictureResponse:
        """
        Gets chat picture
        """
        path = f"/api/{session}/chats/{chatId}/picture"
        params = {"refresh": refresh} if refresh is not None else None
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def get_chat_messages(
        self,
        session: str,
        chatId: str,
        limit: int,
        downloadMedia: Optional[bool] = False,
        offset: Optional[int] = None,
        filter_timestamp_lte: Optional[int] = None,
        filter_timestamp_gte: Optional[int] = None,
        filter_fromMe: Optional[bool] = None,
    ) -> ChatsGetChatMessagesResponse:
        """
        Gets messages in the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages"
        params = {}
        params["downloadMedia"] = downloadMedia
        params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if filter_timestamp_lte is not None:
            params["filter.timestamp.lte"] = filter_timestamp_lte
        if filter_timestamp_gte is not None:
            params["filter.timestamp.gte"] = filter_timestamp_gte
        if filter_fromMe is not None:
            params["filter.fromMe"] = filter_fromMe
        params = params if params else None  # params should be None if empty
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def clear_chat_messages(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Clears all messages from the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages"
        return await self._request("DELETE", path)

    async def get_chat_message(
        self,
        session: str,
        chatId: str,
        messageId: str,
        downloadMedia: Optional[bool] = False,
    ) -> ChatsGetChatMessageResponse:
        """
        Gets message by id
        """
        path = f"/api/{session}/chats/{chatId}/messages/{messageId}"
        params = {"downloadMedia": downloadMedia} if downloadMedia is not None else None
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def delete_chat_message(
        self, session: str, chatId: str, messageId: str
    ) -> httpx.Response:  # type: ignore[override]
        """
        Deletes a message from the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages/{messageId}"
        return await self._request("DELETE", path)

    async def edit_chat_message(
        self,
        session: str,
        chatId: str,
        messageId: str,
        request_body: EditMessageRequest,
    ) -> httpx.Response:  # type: ignore[override]
        """
        Edits a message in the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages/{messageId}"
        return await self._request("PUT", path, json_data=request_body)

    async def pin_chat_message(
        self, session: str, chatId: str, messageId: str, request_body: PinMessageRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Pins a message in the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages/{messageId}/pin"
        return await self._request("POST", path, json_data=request_body)

    async def unpin_chat_message(
        self, session: str, chatId: str, messageId: str
    ) -> httpx.Response:  # type: ignore[override]
        """
        Unpins a message in the chat
        """
        path = f"/api/{session}/chats/{chatId}/messages/{messageId}/unpin"
        return await self._request("POST", path)

    async def archive_chat(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Archive the chat
        """
        path = f"/api/{session}/chats/{chatId}/archive"
        return await self._request("POST", path)

    async def unarchive_chat(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Unarchive the chat
        """
        path = f"/api/{session}/chats/{chatId}/unarchive"
        return await self._request("POST", path)

    async def unread_chat(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Unread the chat
        """
        path = f"/api/{session}/chats/{chatId}/unread"
        return await self._request("POST", path)

    # 📢 Channels Endpoints

    async def list_channels(
        self, session: str, role: Optional[str] = None
    ) -> ChannelsListChannelsResponse:
        """
        Get list of know channels
        """
        path = f"/api/{session}/channels"
        params = {"role": role} if role is not None else None
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def create_channel(
        self, session: str, request_body: CreateChannelRequest
    ) -> ChannelsCreateChannelResponse:
        """
        Create a new channel.
        """
        path = f"/api/{session}/channels"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def get_channel_info(
        self, session: str, channel_id: str
    ) -> ChannelsGetChannelInfoResponse:
        """
        Get the channel info
        """
        path = f"/api/{session}/channels/{channel_id}"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def delete_channel(self, session: str, channel_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Delete the channel.
        """
        path = f"/api/{session}/channels/{channel_id}"
        return await self._request("DELETE", path)

    async def follow_channel(self, session: str, channel_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Follow the channel.
        """
        path = f"/api/{session}/channels/{channel_id}/follow"
        return await self._request("POST", path)

    async def unfollow_channel(self, session: str, channel_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Unfollow the channel.
        """
        path = f"/api/{session}/channels/{channel_id}/unfollow"
        return await self._request("POST", path)

    async def mute_channel(self, session: str, channel_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Mute the channel.
        """
        path = f"/api/{session}/channels/{channel_id}/mute"
        return await self._request("POST", path)

    async def unmute_channel(self, session: str, channel_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Unmute the channel.
        """
        path = f"/api/{session}/channels/{channel_id}/unmute"
        return await self._request("POST", path)

    # 🟢 Status Endpoints

    async def send_text_status(
        self, session: str, request_body: TextStatus
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send text status
        """
        path = f"/api/{session}/status/text"
        return await self._request("POST", path, json_data=request_body)

    async def send_image_status(
        self, session: str, request_body: ImageStatus
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send image status
        """
        path = f"/api/{session}/status/image"
        return await self._request("POST", path, json_data=request_body)

    async def send_voice_status(
        self, session: str, request_body: VoiceStatus
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send voice status
        """
        path = f"/api/{session}/status/voice"
        return await self._request("POST", path, json_data=request_body)

    async def send_video_status(
        self, session: str, request_body: VideoStatus
    ) -> httpx.Response:  # type: ignore[override]
        """
        Send video status
        """
        path = f"/api/{session}/status/video"
        return await self._request("POST", path, json_data=request_body)

    async def delete_status(
        self, session: str, request_body: DeleteStatusRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        DELETE sent status
        """
        path = f"/api/{session}/status/delete"
        return await self._request("POST", path, json_data=request_body)

    # 🏷️ Labels Endpoints

    async def get_all_labels(
        self, session: str
    ) -> ChannelsListChannelsResponse:  # Ideally should be LabelsGetAllLabelsResponse, but using ChannelsListChannelsResponse as a placeholder because LabelsGetAllLabelsResponse is not defined in responses
        """
        Get all labels
        """
        path = f"/api/{session}/labels"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def create_label(
        self, session: str, request_body: LabelBody
    ) -> ChannelsCreateChannelResponse:  # Ideally should be LabelsCreateLabelResponse, but using ChannelsCreateChannelResponse as a placeholder because LabelsCreateLabelResponse is not defined in responses
        """
        Create a new label
        """
        path = f"/api/{session}/labels"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def update_label(
        self, session: str, labelId: str, request_body: LabelBody
    ) -> ChannelsCreateChannelResponse:  # Ideally should be LabelsUpdateLabelResponse, but using ChannelsCreateChannelResponse as a placeholder because LabelsUpdateLabelResponse is not defined in responses
        """
        Update a label
        """
        path = f"/api/{session}/labels/{labelId}"
        response = await self._request("PUT", path, json_data=request_body)
        return response.json()  # type: ignore

    async def delete_label(self, session: str, labelId: str) -> httpx.Response:  # type: ignore[override]
        """
        Delete a label
        """
        path = f"/api/{session}/labels/{labelId}"
        return await self._request("DELETE", path)

    async def get_chat_labels(
        self, session: str, chatId: str
    ) -> ChannelsListChannelsResponse:  # Ideally should be LabelsGetChatLabelsResponse, but using ChannelsListChannelsResponse as a placeholder because LabelsGetChatLabelsResponse is not defined in responses
        """
        Get labels for the chat
        """
        path = f"/api/{session}/labels/chats/{chatId}"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def put_chat_labels(
        self, session: str, chatId: str, request_body: SetLabelsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Save labels for the chat
        """
        path = f"/api/{session}/labels/chats/{chatId}"
        return await self._request("PUT", path, json_data=request_body)

    async def get_chats_by_label(
        self, session: str, labelId: str
    ) -> httpx.Response:  # Ideally should be LabelsGetChatsByLabelResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get chats by label
        """
        path = f"/api/{session}/labels/{labelId}/chats"
        return await self._request("GET", path)

    # 👤 Contacts Endpoints

    async def get_all_contacts(
        self,
        session: str = "default",
        sortBy: Optional[str] = None,
        sortOrder: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> httpx.Response:  # Ideally should be ContactsGetAllContactsResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get all contacts
        """
        path = "/api/contacts/all"
        params = {}
        params["session"] = session
        if sortBy is not None:
            params["sortBy"] = sortBy
        if sortOrder is not None:
            params["sortOrder"] = sortOrder
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params = params if params else None  # params should be None if empty
        return await self._request("GET", path, params=params)

    async def get_contact_info(
        self, session: str, contactId: str
    ) -> httpx.Response:  # Ideally should be ContactsGetContactInfoResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get contact basic info
        """
        path = "/api/contacts"
        params = {"session": session, "contactId": contactId}
        return await self._request("GET", path, params=params)

    async def check_contact_exists(
        self, session: str, phone: str
    ) -> ChattingDeprecatedCheckNumberStatusResponse:
        """
        Check phone number is registered in WhatsApp.
        """
        path = "/api/contacts/check-exists"
        params = {"session": session, "phone": phone}
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def get_contact_about(
        self, session: str, contactId: str
    ) -> httpx.Response:  # Ideally should be ContactsGetContactAboutResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Gets the Contact's "about" info
        """
        path = "/api/contacts/about"
        params = {"session": session, "contactId": contactId}
        return await self._request("GET", path, params=params)

    async def get_contact_profile_picture(
        self, session: str, contactId: str, refresh: Optional[bool] = None
    ) -> httpx.Response:  # Ideally should be ContactsGetContactProfilePictureResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get contact's profile picture URL
        """
        path = "/api/contacts/profile-picture"
        params = {"session": session, "contactId": contactId, "refresh": refresh}
        return await self._request("GET", path, params=params)

    async def block_contact(self, request_body: ContactRequest) -> httpx.Response:  # type: ignore[override]
        """
        Block contact
        """
        path = "/api/contacts/block"
        return await self._request("POST", path, json_data=request_body)

    async def unblock_contact(self, request_body: ContactRequest) -> httpx.Response:  # type: ignore[override]
        """
        Unblock contact
        """
        path = "/api/contacts/unblock"
        return await self._request("POST", path, json_data=request_body)

    # 👥 Groups Endpoints

    async def create_group(
        self, session: str, request_body: CreateGroupRequest
    ) -> httpx.Response:  # Ideally should be GroupsCreateGroupResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Create a new group.
        """
        path = f"/api/{session}/groups"
        return await self._request("POST", path, json_data=request_body)

    async def get_groups(
        self,
        session: str,
        sortBy: Optional[str] = None,
        sortOrder: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> httpx.Response:  # Ideally should be GroupsGetGroupsResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get all groups.
        """
        path = f"/api/{session}/groups"
        params = {}
        if sortBy is not None:
            params["sortBy"] = sortBy
        if sortOrder is not None:
            params["sortOrder"] = sortOrder
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params = params if params else None  # params should be None if empty
        return await self._request("GET", path, params=params)

    async def get_group_join_info(
        self, session: str, code: str
    ) -> GroupsGetGroupJoinInfoResponse:
        """
        Get info about the group before joining.
        """
        path = f"/api/{session}/groups/join-info"
        params = {"code": code}
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def join_group(
        self, session: str, request_body: JoinGroupRequest
    ) -> GroupsJoinGroupResponse:
        """
        Join group via code
        """
        path = f"/api/{session}/groups/join"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def refresh_groups(self, session: str) -> httpx.Response:  # type: ignore[override]
        """
        Refresh groups from the server.
        """
        path = f"/api/{session}/groups/refresh"
        return await self._request("POST", path)

    async def get_group_info(
        self, session: str, group_id: str
    ) -> httpx.Response:  # Ideally should be GroupsGetGroupInfoResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get the group.
        """
        path = f"/api/{session}/groups/{group_id}"
        return await self._request("GET", path)

    async def delete_group(self, session: str, group_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Delete the group.
        """
        path = f"/api/{session}/groups/{group_id}"
        return await self._request("DELETE", path)

    async def set_group_info_admin_only(
        self, session: str, group_id: str, request_body: SettingsSecurityChangeInfo
    ) -> httpx.Response:  # type: ignore[override]
        """
        Updates the group "info admin only" settings.
        """
        path = f"/api/{session}/groups/{group_id}/settings/security/info-admin-only"
        return await self._request("PUT", path, json_data=request_body)

    async def get_group_info_admin_only(
        self, session: str, group_id: str
    ) -> GroupsGetGroupInfoAdminOnlyResponse:
        """
        Get the group's 'info admin only' settings.
        """
        path = f"/api/{session}/groups/{group_id}/settings/security/info-admin-only"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def set_group_messages_admin_only(
        self, session: str, group_id: str, request_body: SettingsSecurityChangeInfo
    ) -> httpx.Response:  # type: ignore[override]
        """
        Update settings - who can send messages
        """
        path = f"/api/{session}/groups/{group_id}/settings/security/messages-admin-only"
        return await self._request("PUT", path, json_data=request_body)

    async def get_group_messages_admin_only(
        self, session: str, group_id: str
    ) -> GroupsGetGroupMessagesAdminOnlyResponse:
        """
        Get settings - who can send messages
        """
        path = f"/api/{session}/groups/{group_id}/settings/security/messages-admin-only"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def leave_group(self, session: str, group_id: str) -> httpx.Response:  # type: ignore[override]
        """
        Leave the group.
        """
        path = f"/api/{session}/groups/{group_id}/leave"
        return await self._request("POST", path)

    async def set_group_description(
        self, session: str, group_id: str, request_body: DescriptionRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Updates the group description.
        """
        path = f"/api/{session}/groups/{group_id}/description"
        return await self._request("PUT", path, json_data=request_body)

    async def set_group_subject(
        self, session: str, group_id: str, request_body: SubjectRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Updates the group subject
        """
        path = f"/api/{session}/groups/{group_id}/subject"
        return await self._request("PUT", path, json_data=request_body)

    async def get_group_invite_code(
        self, session: str, group_id: str
    ) -> GroupsGetGroupInviteCodeResponse:
        """
        Gets the invite code for the group.
        """
        path = f"/api/{session}/groups/{group_id}/invite-code"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def revoke_group_invite_code(
        self, session: str, group_id: str
    ) -> GroupsGetGroupInviteCodeResponse:
        """
        Invalidates the current group invite code and generates a new one.
        """
        path = f"/api/{session}/groups/{group_id}/invite-code/revoke"
        response = await self._request("POST", path)
        return response.json()  # type: ignore

    async def get_group_participants(
        self, session: str, group_id: str
    ) -> httpx.Response:  # Ideally should be GroupsGetGroupParticipantsResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get participants
        """
        path = f"/api/{session}/groups/{group_id}/participants"
        return await self._request("GET", path)

    async def add_group_participants(
        self, session: str, group_id: str, request_body: ParticipantsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Add participants
        """
        path = f"/api/{session}/groups/{group_id}/participants/add"
        return await self._request("POST", path, json_data=request_body)

    async def remove_group_participants(
        self, session: str, group_id: str, request_body: ParticipantsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Remove participants
        """
        path = f"/api/{session}/groups/{group_id}/participants/remove"
        return await self._request("POST", path, json_data=request_body)

    async def promote_group_admin(
        self, session: str, group_id: str, request_body: ParticipantsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Promote participants to admin users.
        """
        path = f"/api/{session}/groups/{group_id}/admin/promote"
        return await self._request("POST", path, json_data=request_body)

    async def demote_group_admin(
        self, session: str, group_id: str, request_body: ParticipantsRequest
    ) -> httpx.Response:  # type: ignore[override]
        """
        Demotes participants to regular users.
        """
        path = f"/api/{session}/groups/{group_id}/admin/demote"
        return await self._request("POST", path, json_data=request_body)

    # ✅ Presence Endpoints

    async def set_presence(
        self, session: str, request_body: WAHASessionPresence
    ) -> httpx.Response:  # type: ignore[override]
        """
        Set session presence
        """
        path = f"/api/{session}/presence"
        return await self._request("POST", path, json_data=request_body)

    async def get_all_presence(
        self, session: str
    ) -> httpx.Response:  # Ideally should be PresenceGetAllPresenceResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get all subscribed presence information.
        """
        path = f"/api/{session}/presence"
        return await self._request("GET", path)

    async def get_presence(self, session: str, chatId: str) -> WAHAChatPresences:
        """
        Get the presence for the chat id.
        """
        path = f"/api/{session}/presence/{chatId}"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def get_all_presence(  # duplicated function - remove
        self, session: str
    ) -> httpx.Response:  # Ideally should be PresenceGetAllPresenceResponse, but httpx.Response is more flexible for now - not defined in responses
        """
        Get all subscribed presence information.
        """
        path = f"/api/{session}/presence"
        return await self._request("GET", path)

    async def subscribe_presence(self, session: str, chatId: str) -> httpx.Response:  # type: ignore[override]
        """
        Subscribe to presence events for the chat.
        """
        path = f"/api/{session}/presence/{chatId}/subscribe"
        return await self._request("POST", path)

    async def set_presence(  # duplicated function - remove
        self, session: str, request_body: WAHASessionPresence
    ) -> httpx.Response:  # type: ignore[override]
        """
        Set session presence
        """
        path = f"/api/{session}/presence"
        return await self._request("POST", path, json_data=request_body)

    # 🖼️ Screenshot Endpoint
    # ... (Screenshot Endpoint remains the same as in the previous response)

    # 🔍 Observability Endpoints

    async def ping_server(self) -> ObservabilityPingResponse:
        """
        Ping the server
        """
        path = "/ping"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def health_check(self) -> httpx.Response:
        """
        Check the health of the server
        """
        path = "/health"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def get_server_version(self) -> ObservabilityServerVersionResponse:
        """
        Get the version of the server
        """
        path = "/api/server/version"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def get_server_environment(
        self, all_env_vars: Optional[bool] = None
    ) -> ObservabilityServerEnvironmentResponse:
        """
        Get the server environment
        """
        path = "/api/server/environment"
        params = {"all": all_env_vars} if all_env_vars is not None else None
        response = await self._request("GET", path, params=params)
        return response.json()  # type: ignore

    async def get_server_status(self) -> ObservabilityServerStatusResponse:
        """
        Get the server status
        """
        path = "/api/server/status"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def stop_server(
        self, request_body: StopRequest
    ) -> ObservabilityStopServerResponse:
        """
        Stop (and restart) the server
        """
        path = "/api/server/stop"
        response = await self._request("POST", path, json_data=request_body)
        return response.json()  # type: ignore

    async def get_debug_heapsnapshot(self) -> ObservabilityDebugHeapsnapshotResponse:
        """
        Return a heapsnapshot (Debug endpoint)
        """
        path = "/api/server/debug/heapsnapshot"
        response = await self._request("GET", path)
        return response.json()  # type: ignore

    async def deprecated_get_version(self) -> ObservabilityDeprecatedGetVersionResponse:
        """
        [DEPRECATED] Get the server version
        """
        path = "/api/version"
        response = await self._request("GET", path)
        self.decrypt_whatsapp_media(media_url="", base64_media_key="", media_type="")
        return response.json()  # type: ignore

    async def decrypt_whatsapp_media(
        self, media_url: str, base64_media_key: str, media_type: MediaType
    ):
        return await decrypt_whatsapp_media(
            media_url=media_url,
            base64_media_key=base64_media_key,
            media_type=media_type,
        )

    async def download_whatsapp_media(self, media_url: str, session: str) -> bytes:
        return await download_whatsapp_file(media_url, self.api_key, session)


# Example usage remains the same, but you can now use the TypedDicts for type hinting:
async def main():
    base_url = "https://messaging.mbras.com.br"  # Replace with your API base URL
    api_key = "9c62d5564345d0b79499a3f6a5dd677bbba48396"  # Replace with your API key

    async with WhatsAppApiClient(base_url, api_key) as client:
        try:
            # Example: Check number status (deprecated, but response is typed)
            check_number_response: ChattingDeprecatedCheckNumberStatusResponse = (
                await client.deprecated_check_number_status(
                    session="default", phone="PHONE_NUMBER"
                )
            )  # Replace with phone number
            print(
                "Check Number Status Code:", check_number_response.status_code
            )  # Still httpx.Response
            print(
                "Check Number Response (parsed):", check_number_response
            )  # Now TypedDict

            # Example: Get chats overview (typed response)
            chats_overview_response: ChatsGetChatsOverviewResponse = (
                await client.get_chats_overview(session="default")
            )
            print(
                "Chats Overview Status Code:", chats_overview_response.status_code
            )  # Still httpx.Response
            print(
                "Chats Overview Response (parsed):", chats_overview_response
            )  # Now List[ChatSummary]

            # Example: Ping server (typed response)
            ping_response: ObservabilityPingResponse = await client.ping_server()
            print(
                "Ping Status Code:", ping_response.status_code
            )  # Still httpx.Response
            print(
                "Ping Response (parsed):", ping_response
            )  # Now PingResponse TypedDict

            # Example: Get presence for a chat (typed response)
            presence_response: WAHAChatPresences = await client.get_presence(
                session="default", chatId="CHAT_ID@c.us"
            )  # Replace with chat ID
            print(
                "Presence Status Code:", presence_response.status_code
            )  # Still httpx.Response
            print(
                "Presence Response (parsed):", presence_response
            )  # Now WAHAChatPresences TypedDict

        except httpx.HTTPError as e:
            print(f"Request failed: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

whatsapp_client = WhatsAppApiClient(
    base_url=config("WHATSAPP_API_URL"), api_key=config("WHATSAPP_API_KEY")
)
