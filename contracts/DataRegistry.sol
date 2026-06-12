// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Simple IPFS registry for anchored records
contract DataRegistry {
    struct Record {
        address author;
        string ipfsHash;
        string title;
        string source;
        uint256 timestamp;
    }

    Record[] public records;
    event Registered(uint256 indexed id, address indexed author, string ipfsHash, uint256 timestamp);

    function register(string calldata ipfsHash, string calldata title, string calldata source) external {
        records.push(Record({
            author: msg.sender,
            ipfsHash: ipfsHash,
            title: title,
            source: source,
            timestamp: block.timestamp
        }));
        uint256 id = records.length - 1;
        emit Registered(id, msg.sender, ipfsHash, block.timestamp);
    }

    function recordsCount() external view returns (uint256) {
        return records.length;
    }

    function getRecord(uint256 id) external view returns (address, string memory, string memory, string memory, uint256) {
        Record storage r = records[id];
        return (r.author, r.ipfsHash, r.title, r.source, r.timestamp);
    }
}
