# card_games — SSA 标签审查

> **数据库**: `card_games`
> **表**: 6
> **列**: 115 总计 (free=114, controlled=1, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `cards`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `artist` | The name of the artist that illustrated the card art. | **controlled** | 个人姓名 |  |
| `asciiName` | The ASCII(opens new window) (Basic/128) code formatted card name with no special unicode characters. | **free** | 实体名称，公开信息 |  |
| `availability` | A list of the card's available printing types. | **free** | 公开/非个人数据 |  |
| `borderColor` | The color of the card border. | **free** | 类别/标签，公开属性 |  |
| `cardKingdomFoilId` | card Kingdom Foil Id | **free** | 标识符，无个人语义 |  |
| `cardKingdomId` | card Kingdom Id | **free** | 标识符，无个人语义 |  |
| `colorIdentity` | A list of all the colors found in manaCost, colorIndicator, and text | **free** | 标识符，无个人语义 |  |
| `colorIndicator` | A list of all the colors in the color indicator (The symbol prefixed to a card's types). | **free** | 类别/标签，公开属性 |  |
| `colors` | A list of all the colors in manaCost and colorIndicator. | **free** | 类别/标签，公开属性 |  |
| `convertedManaCost` | The converted mana cost of the card. Use the manaValue property. | **free** | 公开/非个人数据 |  |
| `duelDeck` | The indicator for which duel deck the card is in. | **free** | 公开/非个人数据 |  |
| `edhrecRank` | The card rank on EDHRec | **free** | 公开/非个人数据 |  |
| `faceConvertedManaCost` | The converted mana cost or mana value for the face for either half or part of the card. | **free** | 公开/非个人数据 |  |
| `faceName` | The name on the face of the card. | **free** | 实体名称，公开信息 |  |
| `flavorName` | The promotional card name printed above the true card name on special cards that has no game functio | **free** | 实体名称，公开信息 |  |
| `flavorText` | The italicized text found below the rules text that has no game function. | **free** | 公开/非个人数据 |  |
| `frameEffects` | The visual frame effects. | **free** | 公开/非个人数据 |  |
| `frameVersion` | The version of the card frame style. | **free** | 公开/非个人数据 |  |
| `hand` | The starting maximum hand size total modifier. | **free** | 聚合/统计数据 |  |
| `hasAlternativeDeckLimit` | If the card allows a value other than 4 copies in a deck. | **free** | 公开/非个人数据 |  |
| `hasContentWarning` | If the card marked by Wizards of the Coast (opens new window) for having sensitive content. See this | **free** | 公开/非个人数据 |  |
| `hasFoil` | If the card can be found in foil | **free** | 公开/非个人数据 |  |
| `hasNonFoil` | If the card can be found in non-foil | **free** | 公开/非个人数据 |  |
| `id` |  | **free** | 标识符，无个人语义 |  |
| `isAlternative` | If the card is an alternate variation to an original printing | **free** | 公开/非个人数据 |  |
| `isFullArt` | If the card has full artwork. | **free** | 公开/非个人数据 |  |
| `isOnlineOnly` | If the card is only available in online game variations. | **free** | 公开/非个人数据 |  |
| `isOversized` | If the card is oversized. | **free** | 公开/非个人数据 |  |
| `isPromo` | If the card is a promotional printing. | **free** | 公开/非个人数据 |  |
| `isReprint` | If the card has been reprinted. | **free** | 公开/非个人数据 |  |
| `isReserved` | If the card is on the Magic: The Gathering Reserved List (opens new window) | **free** | 公开/非个人数据 |  |
| `isStarter` | If the card is found in a starter deck such as Planeswalker/Brawl decks. | **free** | 公开/非个人数据 |  |
| `isStorySpotlight` | If the card is a Story Spotlight card. | **free** | 公开/非个人数据 |  |
| `isTextless` | If the card does not have a text box. | **free** | 公开/非个人数据 |  |
| `isTimeshifted` | If the card is time shifted | **free** | 公开/非个人数据 |  |
| `keywords` | A list of keywords found on the card. | **free** | 公开/非个人数据 |  |
| `layout` | The type of card layout. For a token card, this will be "token" | **free** | 类别/标签，公开属性 |  |
| `leadershipSkills` | A list of formats the card is legal to be a commander in | **free** | 公开/非个人数据 |  |
| `life` | The starting life total modifier. A plus or minus character precedes an integer. | **free** | 聚合/统计数据 |  |
| `loyalty` | The starting loyalty value of the card. | **free** | 公开/非个人数据 |  |
| `manaCost` | The mana cost of the card wrapped in brackets for each value. | **free** | 公开/非个人数据 |  |
| `mcmId` |  | **free** | 标识符，无个人语义 |  |
| `mcmMetaId` |  | **free** | 标识符，无个人语义 |  |
| `mtgArenaId` |  | **free** | 标识符，无个人语义 |  |
| `mtgjsonV4Id` |  | **free** | 标识符，无个人语义 |  |
| `mtgoFoilId` |  | **free** | 标识符，无个人语义 |  |
| `mtgoId` |  | **free** | 标识符，无个人语义 |  |
| `multiverseId` |  | **free** | 标识符，无个人语义 |  |
| `name` | The name of the card. | **free** | 实体名称，公开信息 |  |
| `number` | The number of the card | **free** | 聚合统计数据或计数，非个人级别 |  |
| `originalReleaseDate` | original Release Date | **free** | 日期字段，未关联到特定个人 |  |
| `originalText` | original Text | **free** | 公开/非个人数据 |  |
| `originalType` | original Type | **free** | 类别/标签，公开属性 |  |
| `otherFaceIds` | other Face Ids | **free** | 标识符，无个人语义 |  |
| `power` | The power of the card. | **free** | 公开/非个人数据 |  |
| `printings` | A list of set printing codes the card was printed in, formatted in uppercase. | **free** | 标识符或代码 |  |
| `promoTypes` | A list of promotional types for a card. | **free** | 类别/标签，公开属性 |  |
| `purchaseUrls` | Links that navigate to websites where the card can be purchased. | **free** | 公开网站地址 |  |
| `rarity` | The card printing rarity. | **free** | 类别/标签，公开属性 |  |
| `scryfallId` |  | **free** | 标识符，无个人语义 |  |
| `scryfallIllustrationId` |  | **free** | 标识符，无个人语义 |  |
| `scryfallOracleId` |  | **free** | 标识符，无个人语义 |  |
| `setCode` | The set printing code that the card is from. | **free** | 标识符，无个人语义 |  |
| `side` | The identifier of the card side. | **free** | 标识符，无个人语义 |  |
| `subtypes` | A list of card subtypes found after em-dash. | **free** | 类别/标签，公开属性 |  |
| `supertypes` | A list of card supertypes found before em-dash. | **free** | 类别/标签，公开属性 |  |
| `tcgplayerProductId` |  | **free** | 标识符，无个人语义 |  |
| `text` | The rules text of the card. | **free** | 公开/非个人数据 |  |
| `toughness` | The toughness of the card. | **free** | 公开/非个人数据 |  |
| `type` | The type of the card as visible, including any supertypes and subtypes. | **free** | 类别/标签，公开属性 |  |
| `types` | A list of all card types of the card, including Un-sets and gameplay variants. | **free** | 类别/标签，公开属性 |  |
| `uuid` | The universal unique identifier (v5) generated by MTGJSON. Each entry is unique. | **free** | 标识符，无个人语义 |  |
| `variations` |  | **free** | 公开/非个人数据 |  |
| `watermark` | The name of the watermark on the card. | **free** | 组织/实体公开信息 |  |

## `foreign_data`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `flavorText` | The foreign flavor text of the card. | **free** | 公开/非个人数据 |  |
| `id` | unique id number identifying this row of data | **free** | 标识符，无个人语义 |  |
| `language` | The foreign language of card. | **free** | 公开/非个人数据 |  |
| `multiverseid` | The foreign multiverse identifier of the card. | **free** | 标识符，无个人语义 |  |
| `name` | The foreign name of the card. | **free** | 实体名称，公开信息 |  |
| `text` | The foreign text ruling of the card. | **free** | 公开/非个人数据 |  |
| `type` | The foreign type of the card. Includes any supertypes and subtypes. | **free** | 类别/标签，公开属性 |  |
| `uuid` |  | **free** | 标识符，无个人语义 |  |

## `legalities`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `format` | format of play | **free** | 类别/标签，公开属性 |  |
| `id` | unique id identifying this legality | **free** | 标识符，无个人语义 |  |
| `status` |  | **free** | 类别/标签，公开属性 |  |
| `uuid` |  | **free** | 标识符，无个人语义 |  |

## `rulings`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `date` | date | **free** | 日期字段，未关联到特定个人 |  |
| `id` | unique id identifying this ruling | **free** | 标识符，无个人语义 |  |
| `text` | description about this ruling | **free** | 公开/非个人数据 |  |
| `uuid` |  | **free** | 标识符，无个人语义 |  |

## `set_translations`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | unique id identifying this set | **free** | 标识符，无个人语义 |  |
| `language` | language of this card set | **free** | 公开/非个人数据 |  |
| `setCode` | the set code for this set | **free** | 标识符，无个人语义 |  |
| `translation` | translation of this card set | **free** | 公开/非个人数据 |  |

## `sets`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `baseSetSize` | The number of cards in the set. | **free** | 标识符或代码 |  |
| `block` | The block name the set was in. | **free** | 组织/实体公开信息 |  |
| `booster` | A breakdown of possibilities and weights of cards in a booster pack. | **free** | 公开/非个人数据 |  |
| `code` | The set code for the set. | **free** | 标识符，无个人语义 |  |
| `id` | unique id identifying this set | **free** | 标识符，无个人语义 |  |
| `isFoilOnly` | If the set is only available in foil. | **free** | 公开/非个人数据 |  |
| `isForeignOnly` | If the set is available only outside the United States of America. | **free** | 公开/非个人数据 |  |
| `isNonFoilOnly` | If the set is only available in non-foil. | **free** | 公开/非个人数据 |  |
| `isOnlineOnly` | If the set is only available in online game variations. | **free** | 公开/非个人数据 |  |
| `isPartialPreview` | If the set is still in preview (spoiled). Preview sets do not have complete data. | **free** | 公开/非个人数据 |  |
| `keyruneCode` | The matching Keyrune code for set image icons. | **free** | 标识符，无个人语义 |  |
| `mcmId` | The Magic Card Marketset identifier. | **free** | 标识符，无个人语义 |  |
| `mcmIdExtras` | The split Magic Card Market set identifier if a set is printed in two sets. This identifier represen | **free** | 标识符，无个人语义 |  |
| `mcmName` |  | **free** | 实体名称，公开信息 |  |
| `mtgoCode` | The set code for the set as it appears on Magic: The Gathering Online | **free** | 标识符，无个人语义 |  |
| `name` | The name of the set. | **free** | 实体名称，公开信息 |  |
| `parentCode` | The parent set code for set variations like promotions, guild kits, etc. | **free** | 标识符，无个人语义 |  |
| `releaseDate` | The release date in ISO 8601 format for the set. | **free** | 日期字段，未关联到特定个人 |  |
| `tcgplayerGroupId` | The group identifier of the set on TCGplayer | **free** | 标识符，无个人语义 |  |
| `totalSetSize` | The total number of cards in the set, including promotional and related supplemental products but ex | **free** | 聚合统计数据或计数，非个人级别 |  |
| `type` | The expansion type of the set. | **free** | 类别/标签，公开属性 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/card_games.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
