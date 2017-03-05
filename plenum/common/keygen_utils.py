import os

from plenum.common.config_util import getConfig
from plenum.common.raet import initLocalKeep, isLocalKeepSetup
from plenum.common.z_util import initStackLocalKeys, createCertsFromKeys
from plenum.common.zstack import ZStack


def initKeys(name, baseDir, sigseed, override=False, config=None):
    if not config:
        from plenum.common.config_util import getConfig
        config = getConfig()
    if config.UseZStack:
        pubkey, verkey = initStackLocalKeys(name, baseDir, sigseed,
                                            override=override)
    else:
        pubkey, verkey = initLocalKeep(name, baseDir, sigseed, override)
    print("Public key is", pubkey)
    print("Verification key is", verkey)
    return pubkey, verkey


def areKeysSetup(name, baseDir, config=None):
    config = config or getConfig()
    if config.UseZStack:
        homeDir = ZStack.homeDirPath(baseDir, name)
        verifDirPath = ZStack.verifDirPath(homeDir)
        pubDirPath = ZStack.publicDirPath(homeDir)
        sigDirPath = ZStack.sigDirPath(homeDir)
        secretDirPath = ZStack.secretDirPath(homeDir)
        for d in (verifDirPath, pubDirPath):
            if not os.path.isfile(os.path.join(d, '{}.key'.format(name))):
                return False
        for d in (sigDirPath, secretDirPath):
            if not os.path.isfile(os.path.join(d, '{}.key_secret'.format(name))):
                return False
        return True
    else:
        return isLocalKeepSetup(name, baseDir)


def learnKeysFromOthers(baseDir, nodeName, otherNodes):
    homeDir = ZStack.homeDirPath(baseDir, nodeName)
    verifDirPath = ZStack.verifDirPath(homeDir)
    pubDirPath = ZStack.publicDirPath(homeDir)
    for d in (homeDir, verifDirPath, pubDirPath):
        os.makedirs(d, exist_ok=True)
    for otherNode in otherNodes:
        for stack in (otherNode.nodestack, otherNode.clientstack):
            createCertsFromKeys(verifDirPath, stack.name,
                                stack.verKey)
            createCertsFromKeys(pubDirPath, stack.name,
                                stack.publicKey)

def tellKeysToOthers(node, otherNodes):
    for otherNode in otherNodes:
        for attrName in ('nodestack', 'clientstack'):
            stack = getattr(node, attrName)
            otherStack = getattr(otherNode, attrName)
            createCertsFromKeys(otherStack.verifKeyDir, stack.name,
                                stack.verKey)
            createCertsFromKeys(otherStack.publicKeysDir, stack.name,
                                stack.publicKey)