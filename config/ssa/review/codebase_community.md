# codebase_community — SSA 标签审查

> **数据库**: `codebase_community`
> **表**: 8
> **列**: 71 总计 (free=62, controlled=9, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `badges`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Date` | the date that the user obtained the badge | **free** | 日期字段，未关联到特定个人 |  |
| `Id` | the badge id | **free** | 标识符，无个人语义 |  |
| `Name` | the badge name the user obtained | **free** | 实体名称，公开信息 |  |
| `UserId` | the unique id of the user | **free** | 标识符，无个人语义 |  |

## `comments`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `CreationDate` | the creation date of the comment | **free** | 日期字段，未关联到特定个人 |  |
| `Id` | the comment Id | **free** | 标识符，无个人语义 |  |
| `PostId` | the unique id of the post | **free** | 标识符，无个人语义 |  |
| `Score` | rating score | **free** | 公开/非个人数据 |  |
| `Text` | the detailed content of the comment | **free** | 公开/非个人数据 |  |
| `UserDisplayName` | user's display name | **controlled** | 个人姓名 |  |
| `UserId` | the id of the user who post the comment | **free** | 标识符，无个人语义 |  |

## `postHistory`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Comment` | comments of the post | **free** | 公开/非个人数据 |  |
| `CreationDate` | the creation date of the post | **free** | 日期字段，未关联到特定个人 |  |
| `Id` | the post history id | **free** | 标识符，无个人语义 |  |
| `PostHistoryTypeId` | the id of the post history type | **free** | 标识符，无个人语义 |  |
| `PostId` | the unique id of the post | **free** | 标识符，无个人语义 |  |
| `RevisionGUID` | the revision globally unique id of the post | **free** | 标识符，无个人语义 |  |
| `Text` | the detailed content of the post | **free** | 公开/非个人数据 |  |
| `UserDisplayName` | user's display name | **controlled** | 个人姓名 |  |
| `UserId` | the user who post the post | **free** | 标识符，无个人语义 |  |

## `postLinks`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `CreationDate` | the creation date of the post link | **free** | 日期字段，未关联到特定个人 |  |
| `Id` | the post link id | **free** | 标识符，无个人语义 |  |
| `LinkTypeId` | the id of the link type | **free** | 标识符，无个人语义 |  |
| `PostId` | the post id | **free** | 标识符，无个人语义 |  |
| `RelatedPostId` | the id of the related post | **free** | 标识符，无个人语义 |  |

## `posts`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `AcceptedAnswerId` | the accepted answer id of the post | **free** | 标识符，无个人语义 |  |
| `AnswerCount` | the total number of answers of the post | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Body` | the body of the post | **free** | 公开/非个人数据 |  |
| `ClosedDate` | the closed date of the post | **free** | 日期字段，未关联到特定个人 |  |
| `CommentCount` | the total number of comments of the post | **free** | 聚合统计数据或计数，非个人级别 |  |
| `CommunityOwnedDate` | the community owned date | **free** | 日期字段，未关联到特定个人 |  |
| `CreaionDate` | the creation date of the post | **free** | 日期字段，未关联到特定个人 |  |
| `FavoriteCount` | the total number of favorites of the post | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Id` | the post id | **free** | 标识符，无个人语义 |  |
| `LasActivityDate` | the last activity date | **free** | 日期字段，未关联到特定个人 |  |
| `LastEditDate` | the last edit date | **free** | 日期字段，未关联到特定个人 |  |
| `LastEditorDisplayName` | the display name of the last editor | **controlled** | 个人姓名，可追溯到个人 |  |
| `LastEditorUserId` | the id of the last editor | **free** | 标识符，无个人语义 |  |
| `OwnerDisplayName` | the display name of the post owner | **controlled** | 个人姓名 |  |
| `OwnerUserId` | the id of the owner user | **free** | 标识符，无个人语义 |  |
| `ParentId` | the id of the parent post | **free** | 标识符，无个人语义 |  |
| `PostTypeId` | the id of the post type | **free** | 标识符，无个人语义 |  |
| `Score` | the score of the post | **free** | 公开/非个人数据 |  |
| `Tags` | the tag of the post | **free** | 公开/非个人数据 |  |
| `Title` | the title of the post | **free** | 公开/非个人数据 |  |
| `ViewCount` | the view count of the post | **free** | 聚合统计数据或计数，非个人级别 |  |

## `tags`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Count` | the count of posts that contain this tag | **free** | 聚合统计数据或计数，非个人级别 |  |
| `ExcerptPostId` | the excerpt post id of the tag | **free** | 标识符，无个人语义 |  |
| `Id` | the tag id | **free** | 标识符，无个人语义 |  |
| `TagName` | the name of the tag | **free** | 实体名称，公开信息 |  |
| `WikiPostId` | the wiki post id of the tag | **free** | 标识符，无个人语义 |  |

## `users`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `AboutMe` | the self introduction of the user | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `AccountId` | the unique id of the account | **free** | 标识符，无个人语义 |  |
| `Age` | user's age | **controlled** | 个人身份属性 |  |
| `CreationDate` | the creation date of the user account | **free** | 日期字段，未关联到特定个人 |  |
| `DisplayName` | the user's display name | **controlled** | 个人姓名 |  |
| `DownVotes` | the number of downvotes | **free** | 标识符或代码 |  |
| `Id` | the user id | **free** | 标识符，无个人语义 |  |
| `LastAccessDate` | the last access date of the user account | **free** | 日期字段，未关联到特定个人 |  |
| `Location` | user's location | **free** | 地理坐标，公开数据 |  |
| `ProfileImageUrl` | the profile image url | **controlled** | 个人身份属性 |  |
| `Reputation` | the user's reputation | **free** | 公开/非个人数据 |  |
| `UpVotes` | the number of upvotes | **free** | 标识符或代码 |  |
| `Views` | the number of views | **free** | 标识符或代码 |  |
| `WebsiteUrl` | the website url of the user account | **controlled** | 个人或财务数据，需要受控暴露 |  |

## `votes`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `BountyAmount` | the amount of bounty | **free** | 公开/非个人数据 |  |
| `CreationDate` | the creation date of the vote | **free** | 日期字段，未关联到特定个人 |  |
| `Id` | the vote id | **free** | 标识符，无个人语义 |  |
| `PostId` | the id of the post that is voted | **free** | 标识符，无个人语义 |  |
| `UserId` | the id of the voter | **free** | 标识符，无个人语义 |  |
| `VoteTypeId` | the id of the vote type | **free** | 标识符，无个人语义 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/codebase_community.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
