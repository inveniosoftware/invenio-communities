export const isMember = true;

export const mockedPublicViewData = {
  aggregations: {
    visibility: {
      buckets: [],
    },
    role: {
      buckets: [],
    },
  },
  hits: [
    {
      id: "1",
      member: {
        user: "1",
        name: "Lars Holm Nielsen",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Javier Romero Castro",
        description: "Unversity of Oviedo",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Pablo Garcia Marcos",
        description: "Unversity of Oviedo",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Sergio Nicolas Cuellar",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Karolina Przerwa",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Zacharias Zacharodimos",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Nicola Tarocco",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "it-dep-cda-dr",
        is_group: true,
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
  ],
  total: 6,
};

export const mockedMemberViewData = {
  aggregations: {
    visibility: {
      buckets: [],
    },
    role: {
      buckets: [],
    },
  },
  hits: [
    {
      id: "1",
      member: {
        user: "1",
        name: "Lars Holm Nielsen",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "public",
      role: "owner",
      created: "2022-02-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Javier Romero Castro",
        description: "Unversity of Oviedo",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: true,
      visibility: "hidden",
      role: "member",
      created: "2022-01-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Pablo Garcia Marcos",
        description: "Unversity of Oviedo",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "hidden",
      role: "member",
      created: "2021-02-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Sergio Nicolas Cuellar",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "hidden",
      role: "manager",
      created: "2020-02-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Karolina Przerwa",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "public",
      role: "manager",
      created: "2022-02-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Zacharias Zacharodimos",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "public",
      role: "manager",
      created: "2022-03-01T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "Nicola Tarocco",
        description: "CERN",
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      is_current_user: false,
      visibility: "public",
      role: "owner",
      created: "2022-03-15T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
    {
      id: "1",
      member: {
        user: "1",
        name: "it-dep-cda-dr",
        is_group: true,
        links: {
          self: "",
          self_html: "",
          avatar: "",
        },
      },
      visibility: "public",
      role: "owner",
      created: "2022-03-15T11:01:01Z",
      updated: "2022-02-01T11:12:31Z",
      links: {
        self: "https://127.0.0.1:5000/api/communities/:id/members/:id",
      },
    },
  ],
  total: 6,
};

export const config = {
  visibility: {
    options: [
      {
        title: "Public",
        value: "public", //true or false
        description: "Your community membership is visible to everyone.",
      },
      {
        title: "Hidden",
        value: "hidden",
        description:
          "Your community membership is only visible to other members of the community.",
      },
    ],
  },
  role: {
    options: [
      {
        title: "Reader",
        value: "reader",
        description: "Can view restricted records.",
      },
      {
        title: "Curator",
        value: "curator",
        description: "Can curate records and view restricted records.",
      },
      {
        title: "Manager",
        value: "manager",
        description:
          "Can manage members, curate records and view restricted records.",
      },
      {
        title: "Owner",
        value: "owner",
        description: "Full administrative access to the entire community.",
      },
    ],
  },
};
