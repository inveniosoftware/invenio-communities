export class CommunityLinksExtractor {
  #urls;

  constructor(community) {
    if (!community?.links) {
      throw TypeError("Request resource links are undefined");
    }
    this.#urls = community.links;
  }

  get selfUrl() {
    if (!this.#urls.self) {
      throw TypeError("Self link missing from resource.");
    }
    return this.#urls.self;
  }

  get membersUrl() {
    if (!this.#urls.members) {
      throw TypeError("Members link missing from resource.");
    }
    return this.#urls.members;
  }

  get publicMembersUrl() {
    if (!this.#urls.public_members) {
      throw TypeError("Public members link missing from resource.");
    }
    return this.#urls.public_members;
  }

  get invitations() {
    if (!this.#urls.invitations) {
      throw TypeError("Invitations link missing from resource.");
    }
    return this.#urls.invitations;
  }

  get collectionTreesUrl() {
    if (!this.#urls.collection_trees) {
      throw TypeError("Collection trees link missing from resource.");
    }
    return this.#urls.collection_trees;
  }

  url(key) {
    const urlOfKey = this.#urls[key];
    if (!urlOfKey) {
      throw TypeError(`"${key}" link missing from resource.`);
    }
    return urlOfKey;
  }
}
