# v16-B 거절 지시 두 팔 v16b_dev: gate_failed

```json
{
  "tag": "v16b_dev",
  "label": "J2v16b",
  "report_label": "J1v16b",
  "mode": "dev",
  "judged_with": "once",
  "registered_check": true,
  "verdict": "gate_failed",
  "stop": [],
  "boundary_rule_needed": false,
  "dev_gate": {
    "ko_unanswerable_dev_refusals": {
      "a": 6,
      "b": 0,
      "n": 20,
      "pass": false
    },
    "parts": {
      "ko_unanswerable_dev_refusals": false,
      "C2_false_refusals": false,
      "C2_refusals": false,
      "C3_accuracy": false,
      "C5_you_dont_know": true,
      "C6_generation_p50": true
    },
    "open_test": false
  },
  "final_parts": null,
  "adopt": null,
  "conditions": {
    "C1_test_refusals": null,
    "C2_false_refusals": {
      "en": {
        "a": [],
        "b": [
          "d019",
          "d025",
          "e4064",
          "e4098",
          "e5n27",
          "e5n60"
        ],
        "pass": false
      },
      "ko": {
        "a": [
          "kd025"
        ],
        "b": [],
        "pass": true
      },
      "pass": false
    },
    "C2_refusals": {
      "en": {
        "a": 3,
        "b": 12,
        "pass": false
      },
      "ko": {
        "a": 1,
        "b": 1,
        "pass": true
      },
      "pass": false
    },
    "C3_accuracy": {
      "en": {
        "a": 271,
        "b": 286,
        "diff": 15,
        "n": 72,
        "pass": true,
        "boundary": false,
        "ci90_sum": [
          -2.0,
          33.0
        ],
        "ci90_mean": [
          0.2083,
          -0.0278,
          0.4583
        ]
      },
      "ko": {
        "a": 499,
        "b": 486,
        "diff": -13,
        "n": 112,
        "pass": false,
        "boundary": false,
        "ci90_sum": [
          -26.0,
          0.0
        ],
        "ci90_mean": [
          -0.1161,
          -0.2321,
          0.0
        ]
      },
      "pass": false
    },
    "C4_mixed": {
      "a": [],
      "b": [],
      "scope": "dev",
      "pass": true
    },
    "C5_you_dont_know": {
      "a": [
        "e4002",
        "e4055",
        "e4a08",
        "e5n57"
      ],
      "b": [],
      "scope": "dev",
      "pass": true
    },
    "C6_generation_p50": {
      "a_ms": 5721.310600172728,
      "b_ms": 4995.549799874425,
      "pass": true
    }
  },
  "report": {
    "refusals": {
      "ans": {
        "en": {
          "a": 3,
          "b": 12,
          "n": 75,
          "a_by_kind": {
            "near_miss": {
              "n": 3,
              "refusals": 0
            },
            "other": {
              "n": 72,
              "refusals": 3
            }
          },
          "b_by_kind": {
            "near_miss": {
              "n": 3,
              "refusals": 2
            },
            "other": {
              "n": 72,
              "refusals": 10
            }
          }
        },
        "ko": {
          "a": 1,
          "b": 1,
          "n": 118,
          "a_by_kind": {
            "near_miss": {
              "n": 6,
              "refusals": 0
            },
            "other": {
              "n": 112,
              "refusals": 1
            }
          },
          "b_by_kind": {
            "near_miss": {
              "n": 6,
              "refusals": 0
            },
            "other": {
              "n": 112,
              "refusals": 1
            }
          }
        }
      },
      "na": {
        "en": {
          "a": 14,
          "b": 18,
          "n": 20,
          "a_by_kind": {
            "adjacent": {
              "n": 12,
              "refusals": 12
            },
            "near_miss": {
              "n": 8,
              "refusals": 2
            }
          },
          "b_by_kind": {
            "adjacent": {
              "n": 12,
              "refusals": 12
            },
            "near_miss": {
              "n": 8,
              "refusals": 6
            }
          }
        },
        "ko": {
          "a": 6,
          "b": 0,
          "n": 20,
          "a_by_kind": {
            "adjacent": {
              "n": 12,
              "refusals": 6
            },
            "near_miss": {
              "n": 8,
              "refusals": 0
            }
          },
          "b_by_kind": {
            "adjacent": {
              "n": 12,
              "refusals": 0
            },
            "near_miss": {
              "n": 8,
              "refusals": 0
            }
          }
        }
      }
    },
    "fixed_sentence_use": {
      "a": {
        "en": {
          "none": 95
        },
        "ko": {
          "none": 138
        }
      },
      "b": {
        "en": {
          "exact": 30,
          "none": 65
        },
        "ko": {
          "none": 131,
          "other_language": 7
        }
      }
    },
    "answer_chars_p50": {
      "a": {
        "ans": {
          "en": 1519,
          "ko": 628.5
        },
        "na": {
          "en": 15.0,
          "ko": 241.5
        }
      },
      "b": {
        "ans": {
          "en": 924,
          "ko": 502.0
        },
        "na": {
          "en": 77.0,
          "ko": 95.5
        }
      }
    },
    "generation_p50_ms": {
      "a": {
        "ans": {
          "en": 7955.847300123423,
          "ko": 5171.96830001194
        },
        "na": {
          "en": 1625.1104000257328,
          "ko": 3592.6972499582916
        }
      },
      "b": {
        "ans": {
          "en": 5829.922599950805,
          "ko": 4072.552750003524
        },
        "na": {
          "en": 1460.928300046362,
          "ko": 2503.9739499334246
        }
      }
    },
    "emptied_citations": {
      "a": {
        "ans": 4,
        "na": 20
      },
      "b": {
        "ans": 13,
        "na": 18
      }
    },
    "length_stops": {
      "a": 2,
      "b": 3
    },
    "unanswerable_not_refused": {
      "a": [
        "k4a08",
        "k4a11",
        "k4a15",
        "k4a17",
        "k4a28",
        "e5n15",
        "e5n25",
        "e5n39",
        "e5n40",
        "e5n46",
        "e5n56",
        "k5a08",
        "k5n02",
        "k5n10",
        "k5n17",
        "k5n27",
        "k5n30",
        "k5n33",
        "k5n34",
        "k5n55"
      ],
      "b": [
        "k4a08",
        "k4a11",
        "k4a14",
        "k4a15",
        "k4a17",
        "k4a23",
        "k4a24",
        "k4a26",
        "k4a27",
        "k4a28",
        "e5n15",
        "e5n56",
        "k5a07",
        "k5a08",
        "k5n02",
        "k5n10",
        "k5n17",
        "k5n27",
        "k5n30",
        "k5n33",
        "k5n34",
        "k5n55"
      ]
    },
    "answerable_refused": {
      "a": [
        "d025",
        "kd025",
        "e4002",
        "e4055"
      ],
      "b": [
        "d019",
        "d025",
        "n069",
        "e4002",
        "e4018",
        "e4036",
        "e4053",
        "e4055",
        "e4064",
        "e4089",
        "e4098",
        "e5n27",
        "e5n60"
      ]
    },
    "accuracy_all_answerable": {
      "en": {
        "a": 286,
        "b": 301,
        "n": 75
      },
      "ko": {
        "a": 519,
        "b": 506,
        "n": 118
      }
    },
    "report_label": {
      "C2_false_refusals": {
        "en": {
          "a": [
            "e4055"
          ],
          "b": [
            "e4018",
            "e4036",
            "e4053",
            "e4055",
            "e4064",
            "e4089",
            "e5n60"
          ],
          "pass": false
        },
        "ko": {
          "a": [],
          "b": [],
          "pass": true
        },
        "pass": false
      },
      "C3_accuracy": {
        "en": {
          "a": 337,
          "b": 331,
          "diff": -6,
          "n": 72,
          "pass": false,
          "boundary": false,
          "ci90_sum": [
            -17.0,
            4.0
          ],
          "ci90_mean": [
            -0.0833,
            -0.2361,
            0.0556
          ]
        },
        "ko": {
          "a": 536,
          "b": 521,
          "diff": -15,
          "n": 112,
          "pass": false,
          "boundary": false,
          "ci90_sum": [
            -24.0,
            -6.0
          ],
          "ci90_mean": [
            -0.1339,
            -0.2143,
            -0.0536
          ]
        },
        "pass": false
      },
      "unjudged": {
        "a": 0,
        "b": 0
      }
    }
  },
  "provenance": {
    "git_commit": "559ca177155fe31624c2d5d0e884b005f8d0d73b",
    "files": {
      "v16b_a_qa_dev.gen.jsonl": "3710ece23bbc4cb5c990a57fcc56a915f829a83c42e3d5d9f66c710ee415a7cb",
      "v16b_a_qa_dev.J2v16b.judge.jsonl": "97dcaa20ca906e69500c61d99f05e14155bad208eb3ec3163674fe5f070732b0",
      "v16b_a_qa_dev.J1v16b.judge.jsonl": "d6522a2794f5288e8868d429ff4cf220efad40776aeb392b06671e18501cb840",
      "v16b_a_qa_dev.gen.meta.json": "07fa48fd2102dfab8d8b79a02c670d13ccc4caec747ce9730d2fad7d387b4e64",
      "v16b_a_qa_pool4_dev_en.gen.jsonl": "7883002e91be99320638adedaaa757f99ef33061f61b68311a3a2bc677e7e68f",
      "v16b_a_qa_pool4_dev_en.J2v16b.judge.jsonl": "46e31a8febcede2e860299b9ccbec12a704ff63235a9af180f68d91a2d4eafad",
      "v16b_a_qa_pool4_dev_en.J1v16b.judge.jsonl": "0e5bc8388b553822576cdf585cdc9586760e049610cf0c9d77a2648d15a60c99",
      "v16b_a_qa_pool4_dev_en.gen.meta.json": "e7f9346d8b3438644eed0494f6c28c8c71795286bd63dff2f1f162919f105864",
      "v16b_a_qa_pool5_ans_dev_en.gen.jsonl": "7f80774126695e9fdf71a8094e305d531264ce3c38c8fe33e07def787fa314dc",
      "v16b_a_qa_pool5_ans_dev_en.J2v16b.judge.jsonl": "90894cff2a43f9aea6d8feff0f8de1fc1a03a9609b1d80d32092e5c5ef18e8f3",
      "v16b_a_qa_pool5_ans_dev_en.J1v16b.judge.jsonl": "62711a874f9a6b4cb40445f8f556abdf50c5226986d3eb3793f5b4a62521b2d8",
      "v16b_a_qa_pool5_ans_dev_en.gen.meta.json": "9e18b1f9f087a4fa94163b33c01845ed016499db4f39498cb8eb9c0fe578fade",
      "v16b_a_qa_dev_ko.gen.jsonl": "32aef3a479dc50c87f33aed84c2ce9e0acf9de96a62b7b3193668d020b8a9852",
      "v16b_a_qa_dev_ko.J2v16b.judge.jsonl": "c5a271a83476c8588597fb4b705af1456e0f33dbab698998cd823d0e06f9e35a",
      "v16b_a_qa_dev_ko.J1v16b.judge.jsonl": "af5f4f4b5c7984b5747cfd471d924ba2812cb6c4b1bdb0f677c7be2b963c0dba",
      "v16b_a_qa_dev_ko.gen.meta.json": "e7bc1cf8f2d3a6f7b657723e98361ebd4f5ee123e2a254dc5dd1c52b32fb37ed",
      "v16b_a_qa_dev2_ko.gen.jsonl": "6edd519c70e3d640053d35d7f248bb91a591ffb3b75458491c9f2273331a3d8f",
      "v16b_a_qa_dev2_ko.J2v16b.judge.jsonl": "35ae05a1471e5d5e6181ca49af39f6992bb77572bd5ce39a6e77c93c83a3c579",
      "v16b_a_qa_dev2_ko.J1v16b.judge.jsonl": "e469f5f2cc3a442223d2e46ea79b95afd7d95f3c89e965f27c2f7eac0cec060c",
      "v16b_a_qa_dev2_ko.gen.meta.json": "d9de4d0262590e00d41da87a60fbd956838c0092567b5226865a7590d8b18fee",
      "v16b_a_qa_pool4_dev_ko.gen.jsonl": "2d51d13c54bcd75e371daafa3de242b0fc1c80f0015451c1456d416fe92f5619",
      "v16b_a_qa_pool4_dev_ko.J2v16b.judge.jsonl": "5d1fce2544d9b3125c2560f5dbd6990a25b66bad3d40cebd0dd8dbcd364d5c1a",
      "v16b_a_qa_pool4_dev_ko.J1v16b.judge.jsonl": "c884c35e86f6c47125a19ea1432ce6daceb0ebb4583852ea5b666a6bd6730c3f",
      "v16b_a_qa_pool4_dev_ko.gen.meta.json": "f0e94dd5882ae999d0106d020e6d6ebe51c41c0e04dca4cb405c8de79f2349b6",
      "v16b_a_qa_pool5_ans_dev_ko.gen.jsonl": "a803b623a3efc4e8b9a36d6daf6fc2391f56dc0764d1288a57a1f2a3b92310c0",
      "v16b_a_qa_pool5_ans_dev_ko.J2v16b.judge.jsonl": "c96a5d3a5b211b72b1dfc58f09a3acfe404b57c3787682a97f42ee922e643adc",
      "v16b_a_qa_pool5_ans_dev_ko.J1v16b.judge.jsonl": "253cf86f7ba8c636d93f730249a0616e5f3e02655dd1319073f846bd2663a32d",
      "v16b_a_qa_pool5_ans_dev_ko.gen.meta.json": "9db5f6e214fef124bc2aed02baa1654424ae9d3788e2c94daef0aa6393190f80",
      "v16b_a_qa_pool4_na_dev_en.gen.jsonl": "33e961c5184c3319b580ca2a9f6b4acd2b04bb4cc705e9090d3a54d0b3df7b87",
      "v16b_a_qa_pool4_na_dev_en.gen.meta.json": "c67c044745caa14088f6dd748ae42ece0c5fe1c3f265943d65803a3ab1f7ba6e",
      "v16b_a_qa_pool5_na_dev_en.gen.jsonl": "61497699b6ac05b3296bf876b44a3a2b2573346323f60934292215d11cbf9c7d",
      "v16b_a_qa_pool5_na_dev_en.gen.meta.json": "5413046a1d927305c4d8366918bbe2f1976754e2dd82b58172c3ba1c0aeceda1",
      "v16b_a_qa_pool4_na_dev_ko.gen.jsonl": "43bc74d5e078ba5bf8dedcf211f606180d0485eb93074bd29414aec0eb8c348c",
      "v16b_a_qa_pool4_na_dev_ko.gen.meta.json": "54fde3f2dd4012f604e76e57d89e4e1e69a5e840f7b7473d859fd0c78c139594",
      "v16b_a_qa_pool5_na_dev_ko.gen.jsonl": "d97141d1539dc82402fd27795086d8bc382d326b1c6fa41ccc1afafe3fa62f80",
      "v16b_a_qa_pool5_na_dev_ko.gen.meta.json": "6336aa5e1ce9cb54e4feb5ba4207b4953f31adae561cf76c22bb3a1d958c5bcc",
      "v16b_b_qa_dev.gen.jsonl": "65e3f1dd57622eb1babcf77d0bf0bf95cb92010ef91c314c127ea376f914c754",
      "v16b_b_qa_dev.J2v16b.judge.jsonl": "e9f9c273a3c86f6ac2ba730180187d57d932fdf00d20e09dd36e173cd4d8e181",
      "v16b_b_qa_dev.J1v16b.judge.jsonl": "f31790a466bf430927e85bb51d3ce0e7ce552d9881852aa69c64bd4041901322",
      "v16b_b_qa_dev.gen.meta.json": "7e2b89dce7a6e6a301f5ad96477d835a0d128c021bc8916954a0f0d643127195",
      "v16b_b_qa_pool4_dev_en.gen.jsonl": "1718fa36775d0c565176e315efe660c87b9debfcc4ecfd81f23d7b58916fefe9",
      "v16b_b_qa_pool4_dev_en.J2v16b.judge.jsonl": "3e1851979b128686d4e8e031370ee523016a3e96dc75a64ca3d12356e57a6eae",
      "v16b_b_qa_pool4_dev_en.J1v16b.judge.jsonl": "703d9cb43735926312bf87adb45f42c06d653758753fbad7480c5dd64afd5032",
      "v16b_b_qa_pool4_dev_en.gen.meta.json": "c65461adadc05d28757141978c46e0b702e667d9d6c610bb6c5a98750b57d546",
      "v16b_b_qa_pool5_ans_dev_en.gen.jsonl": "4725ee33d3e17a7e702964cf145e0c68ff4e851ab3acb0d4dd62722596a4098b",
      "v16b_b_qa_pool5_ans_dev_en.J2v16b.judge.jsonl": "209bffcfcfe39fd6695766430592dab1775c4464b30987c9b77ea5026479d545",
      "v16b_b_qa_pool5_ans_dev_en.J1v16b.judge.jsonl": "eb50b2f3b034cc4f1ad74a7548b14330513af8ea62d3887c6e824166ed287fe9",
      "v16b_b_qa_pool5_ans_dev_en.gen.meta.json": "b0cbbde33ff7a9fc1264d29b9a54d0f628595fcea540808a5e6b2d37d6eddac9",
      "v16b_b_qa_dev_ko.gen.jsonl": "190da26625a44dac548c0221473bb92cd888500b33e5120b034c80d111ecc9ee",
      "v16b_b_qa_dev_ko.J2v16b.judge.jsonl": "f003ad1666d7ae44789ba764bd62741a506a51ac77f1bb598bfccd9a8fb89c96",
      "v16b_b_qa_dev_ko.J1v16b.judge.jsonl": "0805f620b78d64985e2f94208278a9f206a2ef64fc2ee83997bc4e7aa8f8559d",
      "v16b_b_qa_dev_ko.gen.meta.json": "aabb300f0383e36c616a1bb957e143515b8a48243d1ade94be52bf58b5e97640",
      "v16b_b_qa_dev2_ko.gen.jsonl": "98ec5fc6e916bd6c15fb731672030ae729fbcf6ad3b54e8cf586659912027b7a",
      "v16b_b_qa_dev2_ko.J2v16b.judge.jsonl": "e9793752996ace43473675a33a49fb0c73ec19d3f0993c30dfa68c408a6fe038",
      "v16b_b_qa_dev2_ko.J1v16b.judge.jsonl": "838ebfbf049fd379ae4bbd80445353efdf008be0e1cb3f85c46e6876338618a8",
      "v16b_b_qa_dev2_ko.gen.meta.json": "444f7805e7757c450039be1ebfb2290d3e0641c19256044ef58868c40cd57e28",
      "v16b_b_qa_pool4_dev_ko.gen.jsonl": "ed1307f72571784ac2b9820e4df2ae03217eea1ce5bdafdeb180809ffe8c36b4",
      "v16b_b_qa_pool4_dev_ko.J2v16b.judge.jsonl": "f5c5a9ebf37f7b92839d6ff166b1e532d560bac7d98a993bf2c11fc8fd9a6512",
      "v16b_b_qa_pool4_dev_ko.J1v16b.judge.jsonl": "18ab4be7cf7157b33e9b697516ca0f9da14b0a5c08b8dbdd5cf9cf1c29e0b334",
      "v16b_b_qa_pool4_dev_ko.gen.meta.json": "7a96f7516c614d2c7ba48a7978d1cafb06e46725402abdc24827c4d419e38df0",
      "v16b_b_qa_pool5_ans_dev_ko.gen.jsonl": "c9411faba64c6b8daa80f1cb4997ca64167d2db65bd412cd609fe4ec6a59b77b",
      "v16b_b_qa_pool5_ans_dev_ko.J2v16b.judge.jsonl": "c700a052ca7b235945f9f3a5ecfa8aa4743806a8e3ee57544aca95a47a8005a9",
      "v16b_b_qa_pool5_ans_dev_ko.J1v16b.judge.jsonl": "b96d3d8af520631bd3d1f4c48d7a3e9ff156e1466901f967bab9e51bce501850",
      "v16b_b_qa_pool5_ans_dev_ko.gen.meta.json": "c2fcb6b3cd47dbbcceb9078c0db8e9afc4ff837c77cd25bb9c6982a57f428a23",
      "v16b_b_qa_pool4_na_dev_en.gen.jsonl": "1495753d98ec7e7a61538bc4183ebfc99c82a89d744ec1f241aaa31d8188a2cf",
      "v16b_b_qa_pool4_na_dev_en.gen.meta.json": "9f0085bc3f3121770c728110f6aa6f046860ce98d20c36d5526f32d85520455f",
      "v16b_b_qa_pool5_na_dev_en.gen.jsonl": "15517db4e245993bd2424fccc6b6b9c4df50dfe805b8f3a8fa77b2428013f396",
      "v16b_b_qa_pool5_na_dev_en.gen.meta.json": "bcbbcb492947d502bdc8a2317d712da0810163b4a5f68c1fdd7c0882afcd9481",
      "v16b_b_qa_pool4_na_dev_ko.gen.jsonl": "d2cdec02823b0754cd432e68630c64812642db103aaa60e600bf67ac7edbdffe",
      "v16b_b_qa_pool4_na_dev_ko.gen.meta.json": "26b0e0c7c1b8a970c260939a621b37829b16ce8c704b2e109c8568edb7f36d04",
      "v16b_b_qa_pool5_na_dev_ko.gen.jsonl": "6597609f65f1bfbdbb51b4fd2ae99fb5d1ab2acbcc9cc720252f5cf6632e6291",
      "v16b_b_qa_pool5_na_dev_ko.gen.meta.json": "5e10700faee82cadbc04dc9a726a09c9d18efdccb23ff5440abebbdff2086599"
    }
  }
}
```
