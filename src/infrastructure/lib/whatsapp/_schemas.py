from typing import TypedDict, List, Optional, Union, Dict, Any, Literal


class Base64File(TypedDict):
    mimetype: str
    data: str


class QRCodeValue(TypedDict):
    value: str


class RequestCodeRequest(TypedDict):
    phoneNumber: str
    method: Optional[str]


class OTPRequest(TypedDict):
    code: str


class CaptchaBody(TypedDict):
    code: str


class MeInfo(TypedDict):
    id: str
    pushName: str


class Map(TypedDict):
    pass  # Represents an empty object for additionalProperties


class ProxyConfig(TypedDict):
    server: str
    username: Optional[str]
    password: Optional[str]


class NowebStoreConfig(TypedDict):
    enabled: bool
    fullSync: bool


class NowebConfig(TypedDict):
    markOnline: bool
    store: NowebStoreConfig


class HmacConfiguration(TypedDict):
    key: str


class RetriesConfiguration(TypedDict):
    delaySeconds: int
    attempts: int
    policy: Literal["linear", "exponential", "constant"]


class CustomHeader(TypedDict):
    name: str
    value: str


class WebhookConfig(TypedDict):
    url: str
    events: List[List[str]]
    hmac: Optional[HmacConfiguration]
    retries: Optional[RetriesConfiguration]
    customHeaders: Optional[List[CustomHeader]]


class SessionConfig(TypedDict):
    metadata: Optional[Map]
    proxy: Optional[ProxyConfig]
    debug: Optional[bool]
    noweb: Optional[NowebConfig]
    webhooks: Optional[List[WebhookConfig]]


class SessionInfo(TypedDict):
    name: str
    me: MeInfo
    assignedWorker: Optional[str]
    status: Literal["STOPPED", "STARTING", "SCAN_QR_CODE", "WORKING", "FAILED"]
    config: Optional[SessionConfig]


class SessionCreateRequest(TypedDict):
    name: str
    start: Optional[bool]
    config: Optional[SessionConfig]


class SessionDTO(TypedDict):
    name: str
    status: Literal["STOPPED", "STARTING", "SCAN_QR_CODE", "WORKING", "FAILED"]
    config: Optional[SessionConfig]


class SessionUpdateRequest(TypedDict):
    config: Optional[SessionConfig]


class SessionStartDeprecatedRequest(TypedDict):
    name: str
    config: Optional[SessionConfig]


class SessionStopDeprecatedRequest(TypedDict):
    name: str
    logout: Optional[bool]


class SessionLogoutDeprecatedRequest(TypedDict):
    name: str


class MessageTextRequest(TypedDict):
    chatId: str
    reply_to: Optional[str]
    text: str
    linkPreview: Optional[bool]
    session: str


class S3MediaData(TypedDict):
    Bucket: str
    Key: str


class WAMedia(TypedDict):
    url: Optional[str]
    mimetype: Optional[str]
    filename: Optional[str]
    s3: Optional[S3MediaData]
    error: Optional[Map]


class WALocation(TypedDict):
    description: Optional[str]
    latitude: str
    longitude: str


class ReplyToMessage(TypedDict):
    id: str
    participant: Optional[str]
    body: Optional[str]


class WAMessage(TypedDict):
    id: str
    timestamp: int
    from_: str
    fromMe: bool
    to: str
    participant: Optional[str]
    body: str
    hasMedia: bool
    media: Optional[WAMedia]
    mediaUrl: Optional[str]  # deprecated
    ack: Literal[-1, 0, 1, 2, 3, 4]
    ackName: str
    author: Optional[str]
    location: Optional[WALocation]
    vCards: Optional[List[str]]
    _data: Optional[Map]
    replyTo: Optional[ReplyToMessage]


class BinaryFile(TypedDict):
    mimetype: str
    filename: Optional[str]
    data: str


class RemoteFile(TypedDict):
    mimetype: str
    filename: Optional[str]
    url: str


File = Union[RemoteFile, BinaryFile]


class MessageImageRequest(TypedDict):
    chatId: str
    file: File
    reply_to: Optional[str]
    caption: Optional[str]
    session: str


class MessageFileRequest(TypedDict):
    chatId: str
    file: File
    reply_to: Optional[str]
    caption: Optional[str]
    session: str


class VoiceBinaryFile(TypedDict):
    mimetype: Optional[str]
    filename: Optional[str]
    data: str


class VoiceRemoteFile(TypedDict):
    mimetype: Optional[str]
    url: str


VoiceFile = Union[VoiceRemoteFile, VoiceBinaryFile]


class MessageVoiceRequest(TypedDict):
    chatId: str
    file: VoiceFile
    reply_to: Optional[str]
    session: str


class VideoRemoteFile(TypedDict):
    mimetype: Optional[str]
    filename: Optional[str]
    url: str


class VideoBinaryFile(TypedDict):
    mimetype: Optional[str]
    filename: Optional[str]
    data: str


VideoFile = Union[VideoRemoteFile, VideoBinaryFile]


class MessageVideoRequest(TypedDict):
    chatId: str
    file: VideoFile
    reply_to: Optional[str]
    asNote: Optional[bool]
    caption: Optional[str]
    session: str


class Button(TypedDict):
    text: str
    id: Optional[str]
    url: Optional[str]
    phoneNumber: Optional[str]
    copyCode: Optional[str]
    type: Literal["reply", "url", "call", "copy"]


class SendButtonsRequest(TypedDict):
    chatId: str
    header: str
    headerImage: Optional[File]
    body: str
    footer: str
    buttons: List[Button]
    session: str


class MessageForwardRequest(TypedDict):
    chatId: str
    messageId: str
    session: str


class SendSeenRequest(TypedDict):
    chatId: str
    messageId: Optional[
        str
    ]  # NOWEB engine only - it's important to mark ALL messages as seen
    participant: Optional[
        str
    ]  # NOWEB engine only - the ID of the user that sent the  message (undefined for individual chats)
    session: str


class ChatRequest(TypedDict):
    chatId: str
    session: str


class MessageReactionRequest(TypedDict):
    messageId: str
    reaction: str
    session: str


class MessageStarRequest(TypedDict):
    messageId: str
    chatId: str
    star: bool
    session: str


class MessagePoll(TypedDict):
    name: str
    options: List[str]
    multipleAnswers: Optional[bool]


class MessagePollRequest(TypedDict):
    chatId: str
    reply_to: Optional[str]
    poll: MessagePoll
    session: str


class MessageLocationRequest(TypedDict):
    chatId: str
    latitude: float
    longitude: float
    title: Optional[str]
    reply_to: Optional[str]
    session: str


class MessageLinkPreviewRequest(TypedDict):
    chatId: str
    session: str
    url: str
    title: Optional[str]


class VCardContact(TypedDict):
    vcard: str


class Contact(TypedDict):
    fullName: str
    organization: Optional[str]
    phoneNumber: str
    whatsappId: Optional[str]
    vcard: Optional[str]


ContactPayload = Union[VCardContact, Contact]


class MessageContactVcardRequest(TypedDict):
    chatId: str
    contacts: List[ContactPayload]
    session: str


class WANumberExistResult(TypedDict):
    chatId: Optional[str]
    numberExists: bool


class MessageReplyRequest(TypedDict):
    chatId: str
    reply_to: Optional[str]
    text: str
    linkPreview: bool
    session: str


class ChatSummary(TypedDict):
    id: str
    name: Optional[str]
    picture: Optional[str]
    lastMessage: Optional[Map]
    _chat: Optional[Map]


class ChatPictureResponse(TypedDict):
    url: str


class PinMessageRequest(TypedDict):
    duration: int


class EditMessageRequest(TypedDict):
    text: str


class Channel(TypedDict):
    id: str
    name: str
    invite: str
    preview: str
    picture: str
    description: Optional[str]
    verified: bool
    role: Literal["OWNER", "ADMIN", "SUBSCRIBER", "GUEST"]


class CreateChannelRequest(TypedDict):
    name: str
    description: str
    picture: Optional[File]


class TextStatus(TypedDict):
    contacts: Optional[List[str]]
    text: str
    backgroundColor: str
    font: int


class ImageStatus(TypedDict):
    file: File
    contacts: Optional[List[str]]
    caption: Optional[str]


class VoiceStatus(TypedDict):
    file: VoiceFile
    contacts: Optional[List[str]]
    backgroundColor: str


class VideoStatus(TypedDict):
    file: VideoFile
    contacts: Optional[List[str]]
    caption: Optional[str]


class DeleteStatusRequest(TypedDict):
    id: str
    contacts: Optional[List[str]]


class Label(TypedDict):
    id: str
    name: str
    color: int
    colorHex: str


class LabelBody(TypedDict):
    name: str
    colorHex: str
    color: Optional[int]


class LabelID(TypedDict):
    id: str


class SetLabelsRequest(TypedDict):
    labels: List[LabelID]


class ContactRequest(TypedDict):
    contactId: str
    session: str


class Participant(TypedDict):
    id: str


class CreateGroupRequest(TypedDict):
    name: str
    participants: List[Participant]


class JoinGroupRequest(TypedDict):
    code: str


class JoinGroupResponse(TypedDict):
    id: str


class SettingsSecurityChangeInfo(TypedDict):
    adminsOnly: bool


class DescriptionRequest(TypedDict):
    description: str


class SubjectRequest(TypedDict):
    subject: str


class ParticipantsRequest(TypedDict):
    participants: List[Participant]


class WAHASessionPresence(TypedDict):
    chatId: str
    presence: Literal["offline", "online", "typing", "recording", "paused"]


class WAHAPresenceData(TypedDict):
    participant: str
    lastSeen: int
    lastKnownPresence: Literal["offline", "online", "typing", "recording", "paused"]


class WAHAChatPresences(TypedDict):
    id: str
    presences: List[WAHAPresenceData]


class PingResponse(TypedDict):
    message: str


class WAHAEnvironment(TypedDict):
    version: str
    engine: str
    tier: str
    browser: str


class WorkerInfo(TypedDict):
    id: str


class ServerStatusResponse(TypedDict):
    startTimestamp: int
    uptime: int
    worker: WorkerInfo


class StopRequest(TypedDict):
    force: bool


class StopResponse(TypedDict):
    stopping: bool


class WASessionStatusBody(TypedDict):
    name: str
    status: Literal["STOPPED", "STARTING", "SCAN_QR_CODE", "WORKING", "FAILED"]


class WAHAWebhookSessionStatus(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WASessionStatusBody
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookMessage(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAMessage
    me: MeInfo
    environment: WAHAEnvironment


class WAReaction(TypedDict):
    text: str
    messageId: str


class WAMessageReaction(TypedDict):
    id: str
    timestamp: int
    from_: str
    fromMe: bool
    to: str
    participant: Optional[str]
    reaction: WAReaction


class WAHAWebhookMessageReaction(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAMessageReaction
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookMessageAny(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAMessage
    me: MeInfo
    environment: WAHAEnvironment


class WAMessageAckBody(TypedDict):
    id: str
    from_: str
    to: str
    participant: Optional[str]
    fromMe: bool
    ack: int  # Literal[-1, 0, 1, 2, 3, 4]
    ackName: str
    _data: Optional[Map]


class WAHAWebhookMessageAck(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAMessageAckBody
    me: MeInfo
    environment: WAHAEnvironment


class WAMessageRevokedBody(TypedDict):
    after: WAMessage
    before: WAMessage


class WAHAWebhookMessageRevoked(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAMessageRevokedBody
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookStateChange(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: Map  # No specific schema for payload in state.change
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookGroupJoin(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: Map  # No specific schema for payload in group.join
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookGroupLeave(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: Map  # No specific schema for payload in group.leave
    me: MeInfo
    environment: WAHAEnvironment


class WAHAPresenceData(TypedDict):
    participant: str
    lastSeen: int
    lastKnownPresence: Literal["offline", "online", "typing", "recording", "paused"]


class WAHAChatPresences(TypedDict):
    id: str
    presences: List[WAHAPresenceData]


class WAHAWebhookPresenceUpdate(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: WAHAChatPresences
    me: MeInfo
    environment: WAHAEnvironment


class PollVote(TypedDict):
    id: str
    selectedOptions: List[str]
    timestamp: int
    to: str
    from_: str
    fromMe: bool


class MessageDestination(TypedDict):
    id: str
    to: str
    from_: str
    fromMe: bool


class PollVotePayload(TypedDict):
    vote: PollVote
    poll: MessageDestination


class WAHAWebhookPollVote(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: PollVotePayload
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookPollVoteFailed(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: PollVotePayload
    me: MeInfo
    environment: WAHAEnvironment


class ChatArchiveEvent(TypedDict):
    id: str
    archived: bool
    timestamp: int


class WAHAWebhookChatArchive(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: ChatArchiveEvent
    me: MeInfo
    environment: WAHAEnvironment


class CallData(TypedDict):
    id: str
    from_: str
    timestamp: int
    isVideo: bool
    isGroup: bool


class WAHAWebhookCallReceived(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: CallData
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookCallAccepted(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: CallData
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookCallRejected(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: CallData
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookLabelUpsert(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: Label
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookLabelDeleted(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: Label
    me: MeInfo
    environment: WAHAEnvironment


class LabelChatAssociation(TypedDict):
    labelId: str
    chatId: str
    label: Optional[Label]


class WAHAWebhookLabelChatAdded(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: LabelChatAssociation
    me: MeInfo
    environment: WAHAEnvironment


class WAHAWebhookLabelChatDeleted(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: LabelChatAssociation
    me: MeInfo
    environment: WAHAEnvironment


class EnginePayload(TypedDict):
    event: str
    data: Optional[Map]


class WAHAWebhookEngineEvent(TypedDict):
    id: str
    session: str
    metadata: Optional[Map]
    engine: Literal["WEBJS", "NOWEB", "GOWS"]
    event: Literal[
        "session.status",
        "message",
        "message.reaction",
        "message.any",
        "message.ack",
        "message.waiting",
        "message.revoked",
        "state.change",
        "group.join",
        "group.leave",
        "presence.update",
        "poll.vote",
        "poll.vote.failed",
        "chat.archive",
        "call.received",
        "call.accepted",
        "call.rejected",
        "label.upsert",
        "label.deleted",
        "label.chat.added",
        "label.chat.deleted",
        "engine.event",
    ]
    payload: EnginePayload
    me: MeInfo
    environment: WAHAEnvironment


# Response Type Aliases (using the TypedDicts defined above)
AuthGetQRResponse = Union[Base64File, QRCodeValue]
AuthGetCaptchaResponse = Union[Base64File]
SessionsListSessionsResponse = List[SessionInfo]
SessionsCreateSessionResponse = SessionDTO
SessionsGetSessionInfoResponse = SessionInfo
SessionsUpdateSessionResponse = SessionDTO
SessionsGetMeResponse = MeInfo
SessionsStartSessionResponse = SessionDTO
SessionsStopSessionResponse = SessionDTO
SessionsLogoutSessionResponse = SessionDTO
SessionsRestartSessionResponse = SessionDTO
SessionsDeprecatedStartSessionResponse = SessionDTO
SessionsDeprecatedStopSessionResponse = SessionDTO
SessionsDeprecatedLogoutSessionResponse = SessionDTO
ChattingSendTextResponse = WAMessage
ChattingSendImageResponse = Dict[str, Any]  # No schema defined, using generic Dict
ChattingSendFileResponse = Dict[str, Any]  # No schema defined, using generic Dict
ChattingSendVoiceResponse = Dict[str, Any]  # No schema defined, using generic Dict
ChattingSendVideoResponse = Dict[str, Any]
ChattingSendButtonsResponse = Dict[str, Any]
ChattingForwardMessageResponse = WAMessage
ChattingSendSeenResponse = Dict[str, Any]
ChattingSetReactionResponse = Dict[str, Any]
ChattingSetStarResponse = Dict[str, Any]
ChattingSendPollResponse = Dict[str, Any]
ChattingSendMessageLocationResponse = Dict[str, Any]
ChattingSendMessageLinkPreviewResponse = Dict[str, Any]
ChattingSendMessageContactVcardResponse = Dict[str, Any]
ChattingDeprecatedGetMessagesResponse = Dict[str, Any]
ChattingDeprecatedCheckNumberStatusResponse = WANumberExistResult
ChattingDeprecatedReplyMessageResponse = Dict[str, Any]
ChatsGetChatsResponse = Dict[str, Any]
ChatsGetChatsOverviewResponse = List[ChatSummary]
ChatsGetChatPictureResponse = ChatPictureResponse
ChatsGetChatMessagesResponse = List[WAMessage]
ChatsGetChatMessageResponse = WAMessage
ChannelsListChannelsResponse = List[Channel]
ChannelsCreateChannelResponse = Channel
ChannelsGetChannelInfoResponse = Channel
GroupsGetGroupJoinInfoResponse = Dict[str, Any]
GroupsJoinGroupResponse = JoinGroupResponse
GroupsGetGroupInfoAdminOnlyResponse = SettingsSecurityChangeInfo
GroupsGetGroupMessagesAdminOnlyResponse = SettingsSecurityChangeInfo
GroupsGetGroupInviteCodeResponse = str
ObservabilityPingResponse = PingResponse
# ObservabilityHealthCheckResponse = HealthCheckResponse
ObservabilityServerVersionResponse = WAHAEnvironment
ObservabilityServerEnvironmentResponse = Dict[str, Any]  # Generic object, no schema
ObservabilityServerStatusResponse = ServerStatusResponse
ObservabilityStopServerResponse = StopResponse
ObservabilityDebugHeapsnapshotResponse = Dict[str, Any]
ObservabilityDeprecatedGetVersionResponse = WAHAEnvironment
